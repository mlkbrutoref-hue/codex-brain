"""Legacy fixture helper disabled: never manufacture a new human approval."""

def main():
    raise RuntimeError('LEGACY_APPROVAL_DISABLED: provide an explicit hash-bound human review and fresh selection evidence')

if __name__=='__main__': main()
