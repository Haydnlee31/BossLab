"""Finite, read-only validation of the project-generated checkpoint."""
import json
import pathlib
import torch
from train_ppo import Policy, ROOT

checkpoint = ROOT / 'artifacts/ppo-smoke.pt'
saved = torch.load(checkpoint, weights_only=True)
policy = Policy()
policy.load_state_dict(saved['state_dict'])
assert saved['steps'] == 4096
assert all(torch.isfinite(p).all() for p in policy.parameters())
obs = torch.zeros(16)
mask = torch.tensor([False, True, False, False, True, False, False])
dist, value = policy(obs, mask)
assert torch.all(dist.probs[~mask] == 0)
assert torch.isclose(dist.probs.sum(), torch.tensor(1.))
clone = Policy()
clone.load_state_dict(torch.load(checkpoint, weights_only=True)['state_dict'])
assert torch.equal(dist.logits, clone(obs, mask)[0].logits)
result = dict(checkpoint=str(checkpoint.relative_to(ROOT)),steps=saved['steps'],finite=True,
              mask_invalid_probability_zero=True,reload_logits_exact=True,torch_version=str(torch.__version__))
(ROOT / 'artifacts/ppo-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
