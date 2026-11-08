"""Bounded, single-environment masked PPO smoke experiment. No second simulator.

Uses installed PyTorch only. Actor sees 16 permitted features; labels/seeds remain
outside actor inputs. See docs/RL.md for limitations and update equations.
"""
import copy
import hashlib
import json
import pathlib
import selectors
import subprocess
import time

import torch
from torch import nn
from torch.distributions import Categorical

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
CONFIG = dict(seed=41, transitions=4096, rollout=512, epochs=3, minibatch=128,
              gamma=.99, gae_lambda=.95, clip=.2, lr=.0003, entropy=.01,
              wall_cap_seconds=1200, environment_processes=1, step_ticks=12,
              architecture=[16, 32, 7], env_version='warden-rl-env-1', core='warden-core-1.0.0')


class Core:
    def __init__(self):
        self.proc = subprocess.Popen(['node', 'ai/bridge.mjs'], cwd=ROOT,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        self.selector = selectors.DefaultSelector()
        self.selector.register(self.proc.stdout, selectors.EVENT_READ)

    def call(self, **message):
        self.proc.stdin.write(json.dumps(message) + '\n')
        self.proc.stdin.flush()
        if not self.selector.select(timeout=10):
            raise TimeoutError('Node combat core did not respond within 10 seconds')
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError('Authoritative Node core exited')
        response = json.loads(line)
        if 'error' in response:
            raise RuntimeError(response['error'])
        return response

    def close(self):
        self.selector.close()
        self.proc.stdin.close()
        try:
            self.proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            self.proc.terminate()
            self.proc.wait(timeout=3)


class Policy(nn.Module):
    def __init__(self):
        super().__init__()
        self.actor = nn.Sequential(nn.Linear(16, 32), nn.Tanh(), nn.Linear(32, 7))
        self.critic = nn.Sequential(nn.Linear(16, 32), nn.Tanh(), nn.Linear(32, 1))

    def forward(self, obs, mask):
        logits = self.actor(obs).masked_fill(~mask, -1e9)
        return Categorical(logits=logits), self.critic(obs).squeeze(-1)


def tensors(state):
    return torch.tensor(state['observation'], dtype=torch.float32), torch.tensor(state['mask'], dtype=torch.bool)


def evaluate(core, policy, identity):
    rows = []
    for scenario_i, scenario in enumerate(['early', 'late', 'switch']):
        for seed in [3001, 3011, 3023]:
            torch.manual_seed(seed + scenario_i * 100)
            state = core.call(op='reset', config=dict(seed=seed, scenario=scenario,
                              controller=identity if identity in ['static', 'adaptive'] else 'ppo-smoke'))
            shaped_return = 0
            while not (state['terminated'] or state['truncated']):
                if policy is None:
                    action = state['mask'].index(True)  # ignored by internal baseline controller
                else:
                    with torch.no_grad():
                        dist, _ = policy(*tensors(state))
                        action = dist.sample().item()
                state = core.call(op='step', action=action)
                shaped_return += state['reward']
            rows.append(dict(policy=identity, seed=seed, scenario=scenario,
                             terminated=state['terminated'], truncated=state['truncated'],
                             reward=shaped_return, report=state['report']))
    return rows


def main():
    torch.set_num_threads(1)
    torch.manual_seed(CONFIG['seed'])
    policy = Policy()
    initial = copy.deepcopy(policy.state_dict())
    optimizer = torch.optim.Adam(policy.parameters(), lr=CONFIG['lr'])
    core = Core()
    updates, episodes, steps = [], [], 0
    start = time.monotonic()
    try:
        state = core.call(op='reset', config=dict(seed=1, scenario='early'))
        episode = 0
        while steps < CONFIG['transitions'] and time.monotonic() - start < CONFIG['wall_cap_seconds']:
            batch = []
            for _ in range(min(CONFIG['rollout'], CONFIG['transitions'] - steps)):
                obs, mask = tensors(state)
                with torch.no_grad():
                    dist, value = policy(obs, mask)
                    action = dist.sample()
                    logp = dist.log_prob(action)
                nxt = core.call(op='step', action=action.item())
                with torch.no_grad():
                    _, nv = policy(*tensors(nxt))
                done = nxt['terminated'] or nxt['truncated']
                batch.append((obs, mask, action, logp, value, nxt['reward'], nv, nxt['terminated'], done))
                steps += 1
                state = nxt
                if done:
                    episodes.append(nxt['report'])
                    episode += 1
                    state = core.call(op='reset', config=dict(seed=1 + episode % 20,
                                      scenario=['early', 'late', 'switch'][episode % 3]))
                if time.monotonic() - start >= CONFIG['wall_cap_seconds']:
                    break
            advantages = []
            gae = torch.tensor(0.)
            for obs, mask, action, logp, value, reward, nv, terminated, done in reversed(batch):
                delta = reward + CONFIG['gamma'] * nv * (not terminated) - value
                gae = delta + CONFIG['gamma'] * CONFIG['gae_lambda'] * (not done) * gae
                advantages.append(gae)
            advantages = torch.stack(list(reversed(advantages))).detach()
            observations = torch.stack([r[0] for r in batch])
            masks = torch.stack([r[1] for r in batch])
            actions = torch.stack([r[2] for r in batch])
            old_logp = torch.stack([r[3] for r in batch]).detach()
            values = torch.stack([r[4] for r in batch]).detach()
            returns = advantages + values
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
            losses = []
            for _ in range(CONFIG['epochs']):
                order = torch.randperm(len(batch))
                for indices in order.split(CONFIG['minibatch']):
                    dist, predicted = policy(observations[indices], masks[indices])
                    ratio = torch.exp(dist.log_prob(actions[indices]) - old_logp[indices])
                    objective = torch.minimum(ratio * advantages[indices], ratio.clamp(.8, 1.2) * advantages[indices])
                    loss = -objective.mean() + .5 * (predicted - returns[indices]).square().mean() - CONFIG['entropy'] * dist.entropy().mean()
                    if not torch.isfinite(loss):
                        raise RuntimeError('Non-finite PPO loss')
                    optimizer.zero_grad()
                    loss.backward()
                    nn.utils.clip_grad_norm_(policy.parameters(), .5)
                    optimizer.step()
                    losses.append(loss.item())
            updates.append(dict(transitions=steps,mean_loss=sum(losses)/len(losses),rollout_reward=sum(r[5] for r in batch)))
            print(json.dumps(updates[-1]), flush=True)
        delta = sum((policy.state_dict()[k] - initial[k]).abs().sum().item() for k in initial)
        actor_delta = sum((policy.state_dict()[k] - initial[k]).abs().sum().item() for k in initial if k.startswith('actor'))
        if not delta > 0 or not actor_delta > 0:
            raise RuntimeError('Parameters did not change')
        checkpoint = OUT / 'ppo-smoke.pt'
        torch.save(dict(state_dict=policy.state_dict(),optimizer=optimizer.state_dict(),config=CONFIG,
                        steps=steps,torch_version=str(torch.__version__)), checkpoint)
        torch.save(dict(state_dict=initial,config=CONFIG,steps=0), OUT / 'ppo-untrained.pt')
        loaded = Policy()
        loaded.load_state_dict(torch.load(checkpoint, weights_only=True)['state_dict'])
        assert all(torch.equal(v, loaded.state_dict()[k]) for k, v in policy.state_dict().items())
        untrained = Policy()
        untrained.load_state_dict(torch.load(OUT / 'ppo-untrained.pt', weights_only=True)['state_dict'])
        training_seconds = time.monotonic() - start
        evaluation = evaluate(core, loaded, 'ppo-smoke') + evaluate(core, untrained, 'untrained') + evaluate(core, None, 'static') + evaluate(core, None, 'adaptive')
        groups = []
        for identity in ['ppo-smoke', 'untrained', 'static', 'adaptive']:
            rows = [r for r in evaluation if r['policy'] == identity]
            groups.append(dict(policy=identity,encounters=len(rows),boss_wins=sum(r['report']['outcome']=='defeat' for r in rows),
                               player_wins=sum(r['report']['outcome']=='victory' for r in rows),truncated=sum(r['truncated'] for r in rows),
                               mean_damage_to_player=sum(r['report']['metrics']['damageToPlayer'] for r in rows)/len(rows),
                               mean_damage_to_boss=sum(r['report']['metrics']['damageToBoss'] for r in rows)/len(rows)))
        result=dict(config=CONFIG,transitions=steps,torch_version=str(torch.__version__),parameter_l1_change=delta,
                    actor_l1_change=actor_delta,finite_losses=True,reload_exact=True,training_seconds=training_seconds,
                    checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),updates=updates,
                    completed_training_episodes=len(episodes),evaluation_groups=groups,evaluation=evaluation,
                    limitation='Smoke experiment; not converged. Custom PPO on maintained PyTorch primitives, not SB3. Browser controller remains disabled.')
        (OUT / 'ppo-training.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ['evaluation','updates']},indent=2))
    finally:
        core.close()


if __name__ == '__main__':
    main()
