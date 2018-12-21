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

from copy import deepcopy

from boac.api.errors import BadRequestError, ForbiddenRequestError, ResourceNotFoundError
from boac.api.util import get_my_cohorts, is_unauthorized_search, strip_analytics
from boac.lib.berkeley import can_view_cohort
from boac.lib.cohort_filter_definition import get_cohort_filter_definitions
from boac.lib.http import tolerant_jsonify
from boac.lib.util import get as get_param, to_bool_or_none as to_bool
from boac.merged import calnet
from boac.merged.student import get_student_query_scope, get_summary_student_profiles
from boac.models.cohort_filter import CohortFilter
from flask import current_app as app, request
from flask_login import current_user, login_required


@app.route('/api/cohorts/my')
@login_required
def my_cohorts():
    return tolerant_jsonify(get_my_cohorts())


@app.route('/api/cohort/filter_definitions')
@login_required
def get_filter_definitions():
    categories = get_cohort_filter_definitions(get_student_query_scope())
    for category in categories:
        for definition in category:
            if definition['type'] == 'array':
                for index, option in enumerate(definition['options']):
                    option['position'] = index
    return tolerant_jsonify(categories)


@app.route('/api/cohorts/all')
@login_required
def all_cohorts():
    cohorts_per_uid = {}
    for cohort in CohortFilter.all_cohorts():
        if can_view_cohort(current_user, cohort):
            for authorized_user in cohort.owners:
                uid = authorized_user.uid
                if uid not in cohorts_per_uid:
                    cohorts_per_uid[uid] = []
                cohorts_per_uid[uid].append(decorate_cohort(cohort, include_students=False))
    owners = []
    for uid in cohorts_per_uid.keys():
        owner = calnet.get_calnet_user_for_uid(app, uid)
        owner.update({
            'cohorts': sorted(cohorts_per_uid[uid], key=lambda c: c['name']),
        })
        owners.append(owner)
    owners = sorted(owners, key=lambda o: (o['firstName'], o['lastName']))
    return tolerant_jsonify(owners)


@app.route('/api/cohort/<cohort_id>/students_with_alerts')
@login_required
def students_with_alerts(cohort_id):
    cohort = CohortFilter.find_by_id(cohort_id)
    if cohort and can_view_cohort(current_user, cohort):
        cohort = decorate_cohort(cohort, include_alerts_for_user_id=current_user.id, include_students=False)
        students = cohort.get('alerts', [])
        alert_sids = [s['sid'] for s in students]
        alert_profiles = get_summary_student_profiles(alert_sids)
        alert_profiles_by_sid = {p['sid']: p for p in alert_profiles}
        for student in students:
            student.update(alert_profiles_by_sid[student['sid']])
            strip_analytics(student)
    else:
        raise ResourceNotFoundError(f'No cohort found with identifier: {cohort_id}')
    return tolerant_jsonify(students)


@app.route('/api/cohort/<cohort_id>')
@login_required
def get_cohort(cohort_id):
    if is_unauthorized_search(request.args):
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    include_students = to_bool(get_param(request.args, 'includeStudents'))
    include_students = True if include_students is None else include_students
    order_by = get_param(request.args, 'orderBy', None)
    offset = get_param(request.args, 'offset', 0)
    limit = get_param(request.args, 'limit', 50)
    cohort = CohortFilter.find_by_id(int(cohort_id))
    if cohort and can_view_cohort(current_user, cohort):
        cohort = decorate_cohort(
            cohort,
            order_by=order_by,
            offset=int(offset),
            limit=int(limit),
            include_alerts_for_user_id=current_user.id,
            include_profiles=True,
            include_students=include_students,
        )
        return tolerant_jsonify(cohort)
    else:
        raise ResourceNotFoundError(f'No cohort found with identifier: {cohort_id}')


@app.route('/api/cohort/create', methods=['POST'])
@login_required
def create_cohort():
    params = request.get_json()
    if is_unauthorized_search(params):
        raise ForbiddenRequestError('You are unauthorized to access student data managed by other departments')
    name = get_param(params, 'name', None)
    if not name:
        raise BadRequestError('Cohort creation requires \'name\'')
    cohort = CohortFilter.create(
        advisor_ldap_uids=get_param(params, 'advisorLdapUids'),
        coe_prep_statuses=get_param(params, 'coePrepStatuses'),
        coe_probation=get_param(params, 'coeProbation'),
        ethnicities=get_param(params, 'ethnicities'),
        genders=get_param(params, 'genders'),
        gpa_ranges=get_param(params, 'gpaRanges'),
        group_codes=get_param(params, 'groupCodes'),
        in_intensive_cohort=to_bool(params.get('inIntensiveCohort')),
        is_inactive_asc=to_bool(params.get('isInactiveAsc')),
        is_inactive_coe=to_bool(params.get('isInactiveCoe')),
        name=name,
        last_name_range=get_param(params, 'lastNameRange'),
        levels=get_param(params, 'levels'),
        majors=get_param(params, 'majors'),
        uid=current_user.get_id(),
        underrepresented=get_param(params, 'underrepresented'),
        unit_ranges=get_param(params, 'unitRanges'),
    )
    return tolerant_jsonify(decorate_cohort(cohort))


@app.route('/api/cohort/update', methods=['POST'])
@login_required
def update_cohort():
    params = request.get_json()
    cohort_id = int(params.get('id'))
    name = params.get('name')
    filter_criteria = params.get('filterCriteria')
    student_count = params.get('studentCount')
    if not name and not filter_criteria and not student_count:
        raise BadRequestError('Invalid request')
    uid = current_user.get_id()
    cohort = next((c for c in CohortFilter.all_owned_by(uid) if c.id == cohort_id), None)
    if not cohort:
        raise ForbiddenRequestError(f'Invalid or unauthorized request')
    name = name or cohort.name
    filter_criteria = filter_criteria or cohort.filter_criteria
    updated = CohortFilter.update(
        cohort_id=cohort_id,
        name=name,
        filter_criteria=filter_criteria,
        student_count=student_count,
    )
    return tolerant_jsonify(decorate_cohort(updated, include_students=False))


@app.route('/api/cohort/delete/<cohort_id>', methods=['DELETE'])
@login_required
def delete_cohort(cohort_id):
    if cohort_id.isdigit():
        cohort_id = int(cohort_id)
        uid = current_user.get_id()
        cohort = next((c for c in CohortFilter.all_owned_by(uid) if c.id == cohort_id), None)
        if cohort:
            CohortFilter.delete(cohort_id)
            return tolerant_jsonify({'message': f'Cohort deleted (id={cohort_id})'}), 200
        else:
            raise BadRequestError(f'User {uid} does not own cohort_filter with id={cohort_id}')
    else:
        raise ForbiddenRequestError(f'Programmatic deletion of canned cohorts is not allowed (id={cohort_id})')


@app.route('/api/cohort/translate_filter_criteria', methods=['POST'])
@login_required
def translate_filter_criteria():
    rows = []
    criteria = get_param(request.get_json(), 'filterCriteria')
    if criteria:
        for definitions in get_cohort_filter_definitions(get_student_query_scope()):
            for definition in definitions:
                selected = criteria.get(definition['key'])
                if selected is not None:
                    if definition['type'] == 'array':
                        for selection in selected:
                            rows.append(_translate_filter_row(definition, selection))
                    else:
                        rows.append(_translate_filter_row(definition, selected))
    return tolerant_jsonify(rows)


def decorate_cohort(cohort, **kwargs):
    cohort_json = cohort.to_api_json(**kwargs)
    uid = current_user.get_id()
    cohort_json.update({'isOwnedByCurrentUser': (uid in [o.uid for o in cohort.owners])})
    return cohort_json


def _translate_filter_row(definition, selection=None):
    clone = deepcopy(definition)
    row = {k: clone.get(k) for k in ['key', 'name', 'options', 'subcategoryHeader', 'type']}
    if definition['type'] == 'array':
        option = next((o for o in row.get('options', []) if o['value'] == selection), None)
        if option:
            row['subcategoryHeader'] = selection
            option['selected'] = True
    else:
        row['value'] = selection
        if definition['type'] == 'range':
            h = row['subcategoryHeader']
            v = row['value']
            row['subcategoryHeader'] = h[0] + ' ' + v[0] + ' ' + h[1] + ' ' + v[1]
        else:
            del row['subcategoryHeader']
    return row
