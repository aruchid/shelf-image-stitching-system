"""Download Middlebury 2003 samples and assess controlled crops plus stereo stress cases."""
import argparse, hashlib, json, sys, subprocess
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from prototype import process

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',type=Path,default=Path('artifacts/public-data'))
 args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
 report={'dataset':'Middlebury 2003 Cones and Teddy, quarter resolution','source':'https://vision.middlebury.edu/stereo/data/scenes2003/','permission':'https://vision.middlebury.edu/stereo/data/','citation':'D. Scharstein and R. Szeliski. High-accuracy stereo depth maps using structured light. CVPR 2003, pp. 195–202.','files':[],'controlled_crops':[],'stereo_stress':[]}
 for scene in ('cones','teddy'):
  images=[]
  for view in ('im2','im6'):
   url=f'https://vision.middlebury.edu/stereo/data/scenes2003/newdata/{scene}/{view}.png'
   path=out/f'{scene}-{view}.png'
   if not path.exists():
    subprocess.run(['curl','--fail','--location','--retry','2','--max-time','60',url,'--output',str(path)],check=True)
   report['files'].append({'path':path.name,'url':url,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
   rgb=plt.imread(path);images.append(np.asarray(rgb[:,:,:3],dtype=float)@np.array([.2126,.7152,.0722]))
  for view,image in zip(('im2','im6'),images):
   for overlap in (40,80,120):
    width=280;start=width-overlap;truth=image[:,:start+width]
    result,found=process(image[:,:width],image[:,start:start+width],20,160)
    rmse=float(np.sqrt(np.mean((result-truth)**2))) if result.shape==truth.shape else None
    report['controlled_crops'].append({'scene':scene,'view':view,'expected_overlap':overlap,'recovered_overlap':found,'rmse':rmse,'passed':found==overlap and rmse is not None and rmse<1e-12})
  left,right=images
  case={'scene':scene,'scope':'Out-of-contract: depth-dependent disparity, not one global translation'}
  try:
   result,found=process(left,right,350,449)
   error=float(np.sqrt(np.mean((left[:,-found:]-right[:,:found])**2)))
   case.update({'accepted':True,'selected_overlap':found,'overlap_rmse':error,'accuracy_claim':None})
   fig,axes=plt.subplots(1,3,figsize=(15,5));
   for ax,img,title in zip(axes,[left,right,result],['Left','Right','Baseline output — not validated panorama']):ax.imshow(img,cmap='gray',vmin=0,vmax=1);ax.set_title(title);ax.axis('off')
   fig.tight_layout();fig.savefig(out/f'{scene}-stress.png',dpi=100);plt.close(fig)
  except ValueError as exc:case.update({'accepted':False,'reason':str(exc)})
  report['stereo_stress'].append(case)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
 if not all(x['passed'] for x in report['controlled_crops']):raise SystemExit('Controlled crop validation failed')
if __name__=='__main__':main()
