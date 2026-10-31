"""平移图像拼接基线 — deterministic numerical prototype."""
import argparse,json
from pathlib import Path
import numpy as np

def finite(a,ndim=None):
 a=np.asarray(a,dtype=float)
 if not np.isfinite(a).all() or not a.size or (ndim is not None and a.ndim!=ndim): raise ValueError('Invalid shape, empty or nonfinite input')
 return a
def process(left,right,overlap_min=12,overlap_max=None):
 left=finite(left,2);right=finite(right,2)
 if left.shape[0]!=right.shape[0]:raise ValueError('Image heights mismatch')
 limit=min(left.shape[1],right.shape[1])-1
 upper=limit if overlap_max is None else min(limit,overlap_max)
 if overlap_min<2 or upper<overlap_min:raise ValueError('Invalid overlap range')
 scores=[]
 for n in range(overlap_min,upper+1):
  a=left[:,-n:].ravel();b=right[:,:n].ravel();a=a-a.mean();b=b-b.mean();den=np.linalg.norm(a)*np.linalg.norm(b)
  scores.append(float(a@b/den) if den>1e-12 else -1.)
 best=overlap_min+int(np.argmax(scores))
 if max(scores)<.1:raise ValueError('No reliable horizontal overlap')
 ramp=np.linspace(0,1,best)[None,:];blend=left[:,-best:]*(1-ramp)+right[:,:best]*ramp
 return np.concatenate([left[:,:-best],blend,right[:,best:]],axis=1),best

def demo():
 rng=np.random.default_rng(42);truth=rng.random((70,240));left=truth[:,:160];right=truth[:,100:];result,overlap=process(left,right,20,100)
 assert overlap==60 and np.allclose(result,truth)
 return None,{'Reconstructed panorama':result,'Left input':left,'Right input':right},{'recovered_overlap_px':overlap,'reconstruction_rmse':float(np.sqrt(np.mean((result-truth)**2)))}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=Path('artifacts'));args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
 x,series,metrics=demo()
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 if x is None:
  fig,axes=plt.subplots(1,len(series),figsize=(14,4),layout='constrained');axes=np.atleast_1d(axes)
  for ax,(label,values) in zip(axes,series.items()):ax.imshow(values,cmap='viridis');ax.set_title(label);ax.set_axis_off()
 else:
  fig,ax=plt.subplots(figsize=(11,5),layout='constrained')
  for label,values in series.items():ax.plot(x,values,label=label)
  ax.legend();ax.grid(alpha=.2)
 fig.suptitle('Synthetic prototype validation — not field measurements')
 fig.savefig(args.output/'result.png',dpi=140);plt.close(fig)
 np.savez_compressed(args.output/'results.npz',**{str(i):v for i,v in enumerate(series.values())})
 (args.output/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
