import test from 'node:test';
import assert from 'node:assert/strict';
import {Environment} from '../ai/environment.mjs';
test('RL adapter shares core, legal masks and delayed actor DTO, truncation distinct',()=>{const e=new Environment();let r=e.reset({seed:9,maxTicks:24});assert.equal(r.observation.length,16);assert(r.observation.every(Number.isFinite));assert.equal(r.mask[6],true);r=e.step(6);assert.equal(r.terminated,false);r=e.step(6);assert.equal(r.truncated,true);assert.equal(r.terminated,false);assert.throws(()=>e.step(6));e.reset();assert.throws(()=>e.step(0));});
