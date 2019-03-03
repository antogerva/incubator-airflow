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
        pass

    @mock.patch('airflow.utils.file.mkdtemp')
    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_without_host_config(self, client_class_mock, mkdtemp_mock):
        pass

    @mock.patch('airflow.operators.docker_operator.tls.TLSConfig')
    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_tls(self, client_class_mock, tls_class_mock):
        pass

    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_unicode_logs(self, client_class_mock):
        pass

    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_container_fails(self, client_class_mock):
        pass

    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_container_fails_no_image_provided(self, client_class_mock):
        pass

    @mock.patch('airflow.utils.file.mkdtemp')
    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_with_host_config_fail(self, client_class_mock, mkdtemp_mock):
        pass

    @staticmethod
    def test_on_kill():
        pass

    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_no_docker_conn_id_no_hook(self, operator_client_mock):
        pass

    @mock.patch('airflow.operators.docker_operator.DockerHook')
    @mock.patch('airflow.operators.docker_operator.APIClient')
    def test_execute_with_docker_conn_id_use_hook(self, operator_client_mock, operator_docker_hook):
        pass


if __name__ == "__main__":
    unittest.main()
