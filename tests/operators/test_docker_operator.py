# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.


import unittest
import logging

try:
    from airflow.operators.docker_operator import DockerOperator
    from airflow.hooks.docker_hook import DockerHook
    from docker import APIClient
except ImportError:
    pass

from airflow.exceptions import AirflowException

try:
    from unittest import mock
except ImportError:
    try:
        import mock
    except ImportError:
        mock = None


class DockerOperatorTestCase(unittest.TestCase):
    @mock.patch('airflow.utils.file.mkdtemp')
    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute(self, client_class_mock, mkdtemp_mock):
        mkdtemp_mock.return_value = '/tmp/mkdtemp'

        host_config = {'binds': ['/host/path:/container/path'],
                       'network_mode': 'bridge',
                       'shm_size': 1000,
                       'mem_limit': None,
                       'auto_remove': False,
                       'dns': None,
                       'dns_search': None
                       }
        container_config = {'image': 'ubuntu:latest',
                            'working_dir': '/container/path',
                            'command': 'echo Hello world!',
                            'environment': {'UNIT': 'TEST'}
                            }

        client_mock = mock.Mock(spec=APIClient)
        client_mock.create_container.return_value = {'Id': 'some_id'}
        client_mock.create_host_config.return_value = host_config
        client_mock.images.return_value = []
        client_mock.logs.return_value = ['container log']
        client_mock.pull.return_value = [b'{"status":"pull log"}']
        client_mock.wait.return_value = {"StatusCode": 0}

        client_class_mock.return_value = client_mock

        operator = DockerOperator(api_version='1.35',
                                  task_id='unittest',
                                  container_config=container_config,
                                  host_config=host_config)
        operator.execute(None)

        client_class_mock.assert_called_with(base_url='unix://var/run/docker.sock', tls=None,
                                             version='1.35')

        client_mock.create_container.assert_called_once_with(
            host_config={'cpu_shares': 1024, 'auto_remove': False,
                         'binds': ['/host/path:/container/path',
                                   '/tmp/mkdtemp:/tmp/airflow'],
                         'network_mode': 'bridge', 'shm_size': 1000, 'mem_limit': None,
                         'dns': None, 'dns_search': None}, image='ubuntu:latest',
            environment={'AIRFLOW_TMP_DIR': '/tmp/airflow', 'UNIT': 'TEST'},
            working_dir='/container/path', command='echo Hello world!'
        )

        client_mock.create_host_config.assert_called_once_with(
            auto_remove=False, binds=['/host/path:/container/path',
                                      '/tmp/mkdtemp:/tmp/airflow'],
            cpu_shares=1024, dns=None, dns_search=None, mem_limit=None,
            network_mode='bridge', shm_size=1000
        )

        client_mock.images.assert_called_with(name='ubuntu:latest')
        client_mock.logs.assert_called_with(container='some_id', stream=True)
        client_mock.pull.assert_called_with('ubuntu:latest', stream=True)
        client_mock.wait.assert_called_with('some_id')

    @mock.patch('airflow.utils.file.mkdtemp')
    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_without_host_config(self, client_class_mock, mkdtemp_mock):
        mkdtemp_mock.return_value = '/tmp/mkdtemp'
        client_mock = mock.Mock(spec=APIClient)
        container_config = {'image': 'ubuntu:latest'}
        client_mock.create_host_config.return_value = {'binds': ['/tmp/mkdtemp:/tmp/airflow'],
                                                       'cpu_shares': 1024}
        client_mock.create_container.return_value = {'Id': 'some_id'}
        client_mock.images.return_value = []
        client_mock.logs.return_value = ['container log']
        client_mock.pull.return_value = [b'{"status":"pull log"}']
        client_mock.wait.return_value = {"StatusCode": 0}
        client_class_mock.return_value = client_mock

        client_class_mock.return_value = client_mock

        operator = DockerOperator(api_version='1.35',
                                  task_id='unittest',
                                  container_config=container_config)
        operator.execute(None)

        client_mock.create_container.assert_called_once_with(
            host_config={'cpu_shares': 1024, 'binds': ['/tmp/mkdtemp:/tmp/airflow']},
            image='ubuntu:latest',
            environment={'AIRFLOW_TMP_DIR': '/tmp/airflow'},
            command=None
        )
        client_mock.create_host_config.assert_called_once_with(
            cpu_shares=1024, binds=['/tmp/mkdtemp:/tmp/airflow']
        )

        client_mock.images.assert_called_with(name='ubuntu:latest')
        client_mock.logs.assert_called_with(container='some_id', stream=True)
        client_mock.pull.assert_called_with('ubuntu:latest', stream=True)
        client_mock.wait.assert_called_with('some_id')

    @mock.patch('airflow.operators.docker_operator.tls.TLSConfig')
    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_tls(self, client_class_mock, tls_class_mock):
        container_config = {'image': 'ubuntu:latest'}
        client_mock = mock.Mock(spec=APIClient)
        client_mock.create_container.return_value = {'Id': 'some_id'}
        client_mock.create_host_config.return_value = mock.Mock()
        client_mock.images.return_value = []
        client_mock.logs.return_value = []
        client_mock.pull.return_value = []
        client_mock.wait.return_value = {"StatusCode": 0}

        client_class_mock.return_value = client_mock
        tls_mock = mock.Mock()
        tls_class_mock.return_value = tls_mock

        operator = DockerOperator(docker_url='tcp://127.0.0.1:2376', task_id='unittest',
                                  tls_client_cert='cert.pem', tls_ca_cert='ca.pem', tls_client_key='key.pem',
                                  container_config=container_config)
        operator.execute(None)

        tls_class_mock.assert_called_with(assert_hostname=None, ca_cert='ca.pem',
                                          client_cert=('cert.pem', 'key.pem'),
                                          ssl_version=None, verify=True)

        client_class_mock.assert_called_with(base_url='https://127.0.0.1:2376',
                                             tls=tls_mock, version=None)

    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_unicode_logs(self, client_class_mock):
        container_config = {'image': 'ubuntu:latest'}
        client_mock = mock.Mock(spec=APIClient)
        client_mock.create_container.return_value = {'Id': 'some_id'}
        client_mock.create_host_config.return_value = mock.Mock()
        client_mock.images.return_value = []
        client_mock.logs.return_value = ['unicode container log 😁']
        client_mock.pull.return_value = []
        client_mock.wait.return_value = {"StatusCode": 0}

        client_class_mock.return_value = client_mock

        originalRaiseExceptions = logging.raiseExceptions
        logging.raiseExceptions = True

        operator = DockerOperator(container_config=container_config, owner='unittest', task_id='unittest')

        with mock.patch('traceback.print_exception') as print_exception_mock:
            operator.execute(None)
            logging.raiseExceptions = originalRaiseExceptions
            print_exception_mock.assert_not_called()

    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_container_fails(self, client_class_mock):
        container_config = {'image': 'ubuntu:latest'}
        client_mock = mock.Mock(spec=APIClient)
        client_mock.create_container.return_value = {'Id': 'some_id'}
        client_mock.create_host_config.return_value = mock.Mock()
        client_mock.images.return_value = []
        client_mock.logs.return_value = []
        client_mock.pull.return_value = []
        client_mock.wait.return_value = {"StatusCode": 1}

        client_class_mock.return_value = client_mock

        operator = DockerOperator(container_config=container_config, owner='unittest', task_id='unittest')

        with self.assertRaises(AirflowException):
            operator.execute(None)

    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_container_fails_no_image_provided(self, client_class_mock):
        container_config = {'network_mode': 'bridge',
                            'shm_size': 1000}
        client_mock = mock.Mock(spec=APIClient)
        client_mock.create_container.return_value = {'Id': 'some_id'}
        client_mock.create_host_config.return_value = mock.Mock()
        client_mock.images.return_value = []
        client_mock.logs.return_value = []
        client_mock.pull.return_value = []
        client_mock.wait.return_value = {"StatusCode": 1}

        client_class_mock.return_value = client_mock

        operator = DockerOperator(container_config=container_config, owner='unittest', task_id='unittest')

        with self.assertRaises(AirflowException):
            operator.execute(None)

    @mock.patch('airflow.utils.file.mkdtemp')
    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_with_host_config_fail(self, client_class_mock, mkdtemp_mock):
        mkdtemp_mock.return_value = '/tmp/test'
        client_mock = mock.Mock(spec=APIClient)
        container_config = {'image': 'ubuntu:latest'}
        client_mock.create_host_config.return_value.side_effect = TypeError('version value passed')
        client_mock.create_container.side_effect = TypeError('version value passed')
        client_mock.images.return_value = []
        client_mock.logs.return_value = ['container log']
        client_mock.pull.return_value = [b'{"status":"pull log"}']
        client_mock.wait.return_value = {"StatusCode": 0}
        client_class_mock.return_value = client_mock
        operator = DockerOperator(api_version='1.35',
                                  task_id='unittest',
                                  container_config=container_config,
                                  host_config={'version': 8,
                                               'auto_remove': False,
                                               'volumes': ['some_dummy_volume:/container/dummy_path']})

        with self.assertRaises(TypeError):
            operator.execute(None)

    @staticmethod
    def test_on_kill():
        client_mock = mock.Mock(spec=APIClient)
        container_config = {'image': 'ubuntu:latest'}
        operator = DockerOperator(container_config=container_config, owner='unittest', task_id='unittest')
        operator.cli = client_mock
        operator.container = {'Id': 'some_id'}

        operator.on_kill()

        client_mock.stop.assert_called_with('some_id')

    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_no_docker_conn_id_no_hook(self, operator_client_mock):
        # Mock out a Docker client, so operations don't raise errors
        container_config = {'image': 'ubuntu:latest'}
        client_mock = mock.Mock(name='DockerOperator.APIClient mock', spec=APIClient)
        client_mock.images.return_value = []
        client_mock.create_container.return_value = {'Id': 'some_id'}
        client_mock.logs.return_value = []
        client_mock.pull.return_value = []
        client_mock.wait.return_value = {"StatusCode": 0}
        operator_client_mock.return_value = client_mock

        # Create the DockerOperator
        operator = DockerOperator(
            container_config=container_config,
            owner='unittest',
            task_id='unittest'
        )

        # Mock out the DockerHook
        hook_mock = mock.Mock(name='DockerHook mock', spec=DockerHook)
        hook_mock.get_conn.return_value = client_mock
        operator.get_hook = mock.Mock(
            name='DockerOperator.get_hook mock',
            spec=DockerOperator.get_hook,
            return_value=hook_mock
        )

        operator.execute(None)
        self.assertEqual(
            operator.get_hook.call_count, 0,
            'Hook called though no docker_conn_id configured'
        )

    @mock.patch('airflow.operators.docker_operator.DockerHook')
    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_with_docker_conn_id_use_hook(self, operator_client_mock,
                                                  operator_docker_hook):
        container_config = {'image': 'ubuntu:latest'}
        # Mock out a Docker client, so operations don't raise errors
        client_mock = mock.Mock(name='DockerOperator.APIClient mock', spec=APIClient)
        client_mock.images.return_value = []
        client_mock.create_container.return_value = {'Id': 'some_id'}
        client_mock.logs.return_value = []
        client_mock.pull.return_value = []
        client_mock.wait.return_value = {"StatusCode": 0}
        operator_client_mock.return_value = client_mock

        # Create the DockerOperator
        operator = DockerOperator(
            container_config=container_config,
            owner='unittest',
            task_id='unittest',
            docker_conn_id='some_conn_id'
        )

        # Mock out the DockerHook
        hook_mock = mock.Mock(name='DockerHook mock', spec=DockerHook)
        hook_mock.get_conn.return_value = client_mock
        operator_docker_hook.return_value = hook_mock

        operator.execute(None)

        self.assertEqual(
            operator_client_mock.call_count, 0,
            'Client was called on the operator instead of the hook'
        )
        self.assertEqual(
            operator_docker_hook.call_count, 1,
            'Hook was not called although docker_conn_id configured'
        )
        self.assertEqual(
            client_mock.pull.call_count, 1,
            'Image was not pulled using operator client'
        )


if __name__ == "__main__":
    unittest.main()
