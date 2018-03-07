"""
Copyright ©2018. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""


import io

from boac.externals import data_loch
from boac.lib.mockingdata import MockRows, register_mock
import pytest


@pytest.mark.usefixtures('db_session')
class TestDataLoch:

    def test_course_page_views_fixture(self, app):
        data = data_loch._get_course_page_views(7654321)
        assert len(data) > 0
        assert {'uid': '61889', 'canvas_user_id': 9000100, 'loch_page_views': 766} in data

    def test_on_time_submissions_relative_to_user_fixture(self, app):
        data = data_loch.get_on_time_submissions_relative_to_user(7654321, 9000100)
        assert len(data) > 0
        assert {'canvas_user_id': 9000100, 'on_time_submissions': 7} in data

    def test_override_fixture(self, app):
        mr = MockRows(io.StringIO('uid,canvas_user_id,loch_page_views\n2040,99999,13'))
        with register_mock(data_loch._get_course_page_views, mr):
            data = data_loch._get_course_page_views(123)
        assert len(data) == 1
        assert {'uid': '2040', 'canvas_user_id': 99999, 'loch_page_views': 13} == data[0]

    def test_fixture_not_found(self, app):
        no_db = data_loch._get_course_page_views(0)
        assert no_db is None