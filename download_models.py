"""Fetch the pinned embedding, reranker and BERT checkpoints plus reranker code."""
import json,os
from pathlib import Path
HERE=Path(__file__).resolve().parent
os.environ['HF_HOME']=str(HERE/'.cache/huggingface')
os.environ['HF_HUB_DISABLE_XET']='1'
def main():
    from huggingface_hub import snapshot_download
    import huggingface_hub.file_download as files
    files.are_symlinks_supported=lambda cache_dir=None:False
    models=json.loads((HERE/'models.json').read_text(encoding='utf-8'))
    for role,m in models.items():
        snapshot_download(m['repo'],revision=m['revision'],local_dir=HERE/m['path'],
            ignore_patterns=['training_args.bin','optimizer.pt','scheduler.pt','rng_state.pth','checkpoint-*/*'])
        print('Ready:',role,flush=True)
    revision='40ced75c3017eb27626c9d4ea981bde21a2662f4'
    snapshot=snapshot_download('Alibaba-NLP/new-impl',revision=revision)
    # Original CrossEncoder auto_map resolves code at main; explicitly lock this
    # local cache ref to the recorded implementation revision for offline use.
    repo=Path(snapshot).parent.parent;refs=repo/'refs';refs.mkdir(exist_ok=True)
    (refs/'main').write_text(revision,encoding='utf-8')
    print('Pinned reranker implementation:',revision)
if __name__=='__main__':main()
