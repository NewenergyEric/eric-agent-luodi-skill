import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import client_setup as cs
from tools import computer_guide as guide


def brief(location='local', system='windows', access='local'):
    return {'schema':1, 'target':{'location':location,'os':system,'access':access},
            'agent':'undecided','first_task':'to_define'}


class ComputerGuideTests(unittest.TestCase):
    def test_local_windows_uses_local_executor_without_claiming_installation(self):
        result = guide.plan(brief(), 'configure', 'sample', 'desk', host_os='Windows')
        self.assertEqual(result['access_route'], 'local_executor_no_ssh_needed')
        self.assertEqual(result['current_executable_scope'], ['windows_local_synthetic_package'])
        self.assertFalse(result['changes_applied'])
        self.assertFalse(result['deployment_ready'])
        self.assertFalse(result['requested_instance']['identity_verified'])
        self.assertEqual(result['acceptance']['agent_loading'], 'not_verified')

    def test_other_machine_reuses_existing_access_but_never_claims_verified(self):
        result = guide.plan(brief('other','windows','existing'), 'configure','sample','desk',host_os='Windows')
        self.assertEqual(result['access_route'], 'reuse_authorized_connection')
        self.assertIn('remote_access_not_verified',result['blockers'])
        self.assertFalse(result['target_inspected'])
        self.assertEqual(result['current_executable_scope'],[])

    def test_missing_remote_access_is_a_blocker(self):
        result = guide.plan(brief('other','macos','none'),'configure','sample','desk',host_os='Windows')
        self.assertIn('remote_access_required',result['blockers'])
        self.assertIn('macos_execution_not_implemented',result['blockers'])

    def test_macos_branch_is_not_advertised_as_a_working_installer(self):
        result = guide.plan(brief('local','macos','local'),'update','sample','desk',host_os='Darwin')
        self.assertEqual(result['current_executable_scope'],[])
        self.assertIn('macos_execution_not_implemented',result['blockers'])
        self.assertNotIn('declared_os_does_not_match_local_executor',result['blockers'])

    def test_os_claim_must_match_actual_local_executor(self):
        result = guide.plan(brief(),'check','sample','desk',host_os='Darwin')
        self.assertIn('declared_os_does_not_match_local_executor',result['blockers'])
        self.assertEqual(result['current_executable_scope'],[])

    def test_secret_fields_and_inconsistent_targets_are_rejected_without_echo(self):
        value = brief()
        value['password'] = 'SYNTHETIC-'+'PRIVATE-VALUE'
        with self.assertRaisesRegex(cs.SetupError,'^invalid_computer_brief$'):
            guide.plan(value,'configure','sample','desk')
        with self.assertRaisesRegex(cs.SetupError,'^inconsistent_target_access$'):
            guide.plan(brief('other','windows','local'),'configure','sample','desk')
        value=brief(); value['target']['host']='synthetic.example.invalid'
        with self.assertRaisesRegex(cs.SetupError,'^invalid_computer_brief$'):
            guide.plan(value,'configure','sample','desk')

    def test_path_escape_rejected_before_read(self):
        with patch.object(cs,'read') as read:
            with self.assertRaises(cs.SetupError):
                guide.from_file('../outside.json','configure','sample','desk')
            read.assert_not_called()

    def test_all_three_cli_entries_are_read_only_and_do_not_construct_engine(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); (root/'brief.json').write_bytes(cs.encode(brief()))
            before=(root/'brief.json').stat().st_mtime_ns
            with patch.object(cs,'ROOT',root),patch.object(cs,'Engine',side_effect=AssertionError('engine must not run')):
                for action in ('configure','check','update'):
                    output=io.StringIO()
                    with contextlib.redirect_stdout(output):
                        code=cs.main([action,'--customer','sample','--brief','brief.json'])
                    self.assertEqual(code,0)
                    result=json.loads(output.getvalue())
                    self.assertEqual(result['status'],'guidance_only')
                    self.assertEqual(result['action'],action)
            self.assertEqual([p.name for p in root.iterdir()],['brief.json'])
            self.assertEqual(before,(root/'brief.json').stat().st_mtime_ns)

    def test_guidance_cannot_be_approved_into_execution(self):
        with patch.object(cs,'Engine',side_effect=AssertionError('engine must not run')):
            output=io.StringIO()
            with contextlib.redirect_stdout(output):
                code=cs.main(['configure','--customer','sample','--brief','examples/computer-local.json','--approve','0'*64])
            self.assertEqual(code,2)
            self.assertEqual(json.loads(output.getvalue())['error'],'guidance_is_read_only')


if __name__=='__main__':
    unittest.main()
