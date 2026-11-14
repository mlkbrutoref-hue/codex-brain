"""Bounded HTTP read transport. No automatic retries, raw errors or request logging."""
import multiprocessing as mp
import urllib.request
import urllib.error
from app.operational.deadlines import OperationalStop


def _request(pipe, endpoint, payload, headers, timeout):
    try:
        request=urllib.request.Request(endpoint,data=payload,headers=headers,method='POST')
        try:
            with urllib.request.urlopen(request,timeout=timeout) as response:
                body=response.read(4_194_305)
                if len(body)>4_194_304: raise ValueError('RESPONSE_TOO_LARGE')
                pipe.send(('HTTP',response.status,response.headers.get('Retry-After'),body))
        except urllib.error.HTTPError as error:
            pipe.send(('HTTP',error.code,error.headers.get('Retry-After'),b''))
    except BaseException:
        pipe.send(('ERROR',None,None,b''))
    finally: pipe.close()


class BoundedHTTPTransport:
    def __call__(self,endpoint,payload,headers,deadline,max_seconds):
        context=mp.get_context('spawn'); parent,child=context.Pipe()
        timeout=deadline.child_timeout(max_seconds)
        process=context.Process(target=_request,args=(child,endpoint,payload,headers,timeout),daemon=True)
        process.start(); child.close()
        try:
            while not parent.poll(min(.1,deadline.child_timeout(max_seconds))):
                deadline.raise_if_expired()
                if not process.is_alive(): raise OperationalStop('HTTP_PROCESS_LOST')
                timeout-=.1
                if timeout<=0: raise OperationalStop('HTTP_TIMEOUT')
            result=parent.recv(); deadline.raise_if_expired()
            if result[0]!='HTTP':raise OperationalStop('HTTP_NETWORK_UNKNOWN')
            return result[1:]
        finally:
            if process.is_alive():process.terminate()
            process.join(timeout=1)
            if process.is_alive():process.kill(); process.join(timeout=1)
            parent.close()
