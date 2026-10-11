"""Deterministic, read-only target routing. This module does not install or connect."""
from __future__ import annotations

import platform

import client_setup as cs


def select(value, choices):
    if not isinstance(value, str) or value not in choices:
        cs.fail('invalid_computer_brief')
    return value


def plan(brief, action, customer, instance, host_os=None):
    cs.identifier(customer)
    cs.identifier(instance)
    select(action, ('configure', 'check', 'update'))
    if not isinstance(brief, dict) or set(brief) != {'schema', 'target', 'agent', 'first_task'}:
        cs.fail('invalid_computer_brief')
    if type(brief['schema']) is not int or brief['schema'] != 1:
        cs.fail('invalid_computer_brief')
    target = brief['target']
    if not isinstance(target, dict) or set(target) != {'location', 'os', 'access'}:
        cs.fail('invalid_computer_brief')
    location = select(target['location'], ('local', 'other', 'unknown'))
    system = select(target['os'], ('windows', 'macos', 'unknown'))
    access = select(target['access'], ('local', 'existing', 'none', 'unknown'))
    agent = select(brief['agent'], ('codex', 'openclaw', 'hermes', 'undecided'))
    task = select(brief['first_task'], ('user_defined', 'to_define'))
    if (location == 'local' and access != 'local') or (location != 'local' and access == 'local'):
        cs.fail('inconsistent_target_access')
    observed = {'Windows': 'windows', 'Darwin': 'macos'}.get(host_os or platform.system(), 'other')
    steps, blockers = [], []
    if location == 'local':
        steps.append('verify_local_instance_and_permission')
        if system != 'unknown' and observed != system:
            blockers.append('declared_os_does_not_match_local_executor')
        access_route = 'local_executor_no_ssh_needed'
    elif location == 'other':
        access_route = 'reuse_authorized_connection' if access == 'existing' else 'user_guided_access_needed'
        steps.append('verify_target_identity_and_authorized_access')
        blockers.append('remote_access_not_verified' if access == 'existing' else 'remote_access_required')
    else:
        access_route = 'identify_target_first'
        blockers.append('target_location_unknown')
    if system == 'unknown':
        blockers.append('target_os_unknown')
    if system == 'macos':
        blockers.append('macos_execution_not_implemented')
    if agent == 'undecided':
        blockers.append('agent_choice_required')
    if task == 'to_define':
        blockers.append('first_real_task_required')
    steps += ['review_environment_and_pinned_dependencies', 'review_network_requirements',
              'review_pinned_agent_recipe', 'show_diff_and_recovery_before_approval',
              'configure_project_skills_preserving_overrides', 'verify_installation_loading_and_task_separately',
              'save_receipt_for_next_conversation']
    blockers += ['dependency_installer_not_implemented', 'network_diagnostics_not_implemented',
                 'real_agent_adapter_not_implemented', 'agent_skill_loading_not_verified', 'real_task_not_run']
    eligible = location == 'local' and system == 'windows' and observed == 'windows'
    return {
        'schema': 1, 'status': 'guidance_only', 'action': action,
        'requested_instance': {'customer': customer, 'instance': instance, 'identity_verified': False},
        'target': dict(target), 'executor_os': observed, 'agent': agent,
        'access_route': access_route, 'target_inspected': False,
        'changes_applied': False, 'deployment_ready': False,
        'current_executable_scope': ['windows_local_synthetic_package'] if eligible else [],
        'next_steps': steps, 'blockers': blockers,
        'acceptance': {'installation': 'not_run', 'agent_loading': 'not_verified', 'real_task': 'not_run'},
    }


def from_file(name, action, customer, instance):
    # Relative project paths only; no credentials, commands, addresses or free text accepted.
    return plan(cs.parse(cs.read(cs.safe(cs.ROOT, name))), action, customer, instance)
