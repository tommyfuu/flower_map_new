from coco import COCO
from cocoeval import COCOeval
import numpy as np
annType = ['segm','bbox','keypoints']
annType = annType[0]
print(annType)
annFile = '/mnt/biology/donaldson/tom/flower_map_new/trial3_gt.json'
cocoGt=COCO(annFile)
resFile = '/mnt/biology/donaldson/tom/flower_map_new/trial3_preds.json'
cocoDt = COCO(resFile)
cocoEval = COCOeval(cocoGt,cocoDt,annType)
cocoEval.evaluate()
cocoEval.accumulate()
cocoEval.summarize()
print("AAAAA")
print(cocoEval.stats)
print(type(cocoEval.stats))
current_stats = list(cocoEval.stats)
current_stat_text = ' Average Precision  (AP) @[ IoU=0.50:0.95 | area=   all | maxDets=100 ] = ' + str(current_stats[0]) + '\n'

print(current_stat_text)