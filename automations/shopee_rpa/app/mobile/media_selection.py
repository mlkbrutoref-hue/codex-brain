from dataclasses import dataclass
from app.media.identity import valid_hash, file_sha256
import time


@dataclass(frozen=True)
class MediaSelectionEvidence:
    expected_hash: str
    thumbnail_evidence: dict
    duration_ms: int
    inventory_snapshot: list
    selected_cell: dict
    visual_identity_review: dict | None = None

    def unambiguous(self, expected_path):
        index=self.selected_cell.get('index')
        if not valid_hash(self.expected_hash) or not isinstance(index,int) or not 0<=index<len(self.inventory_snapshot):
            return False
        row=self.inventory_snapshot[index]
        if row.get('video_path') != expected_path or row.get('duration_ms') != self.duration_ms:
            return False
        thumbnail=self.thumbnail_evidence
        thumbnail_valid=bool(thumbnail.get('asset_sha256')==self.expected_hash and valid_hash(thumbnail.get('sha256')) and
                    thumbnail.get('path') and file_sha256(thumbnail['path'])==thumbnail['sha256'])
        if not thumbnail_valid:return False
        if sum(abs(n.get('duration_ms',0)-self.duration_ms)<=1100 for n in self.inventory_snapshot[:6]) == 1:
            return True
        # Similar durations are insufficient identity. Require a separate visual
        # comparison bound to the selected screenshot and prepared file, before Next.
        review=self.visual_identity_review or {}
        return bool(index<6 and sum(n.get('video_path')==expected_path for n in self.inventory_snapshot)==1 and
                    review.get('status')=='PASS' and review.get('reviewer') and review.get('selected_index')==index and
                    0<=time.time()-review.get('reviewed_at',0)<=1800 and
                    review.get('prepared_sha256')==self.expected_hash and review.get('prepared_path') and
                    file_sha256(review['prepared_path'])==self.expected_hash and
                    review.get('selected_screenshot_sha256')==thumbnail['sha256'] and
                    review.get('reference_path') and valid_hash(review.get('reference_sha256')) and
                    file_sha256(review['reference_path'])==review['reference_sha256'])


def selection_unambiguous(evidence, expected_path, expected_hash):
    try:
        return MediaSelectionEvidence(expected_hash,evidence['thumbnail_evidence'],evidence['duration_ms'],
            evidence['inventory_snapshot'],evidence['selected_cell'],evidence.get('visual_identity_review')).unambiguous(expected_path)
    except (KeyError,TypeError,ValueError,OSError):
        return False
