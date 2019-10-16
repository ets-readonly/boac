import axios from 'axios';
import store from '@/store';
import utils from '@/api/api-utils';

export function cancel(appointmentId, cancelReason, cancelReasonExplained) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/cancel`, {
      cancelReason,
      cancelReasonExplained
    })
    .then(response => {
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} canceled a drop-in appointment`,
        action: 'cancel'
      });
      return response.data
    }, () => null);
}

export function checkIn(
    advisorDeptCodes,
    advisorName,
    advisorRole,
    advisorUid,
    appointmentId
) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/check_in`, {
      advisorDeptCodes,
      advisorName,
      advisorRole,
      advisorUid
    }).then(response => {
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} checked in a drop-in appointment`,
        action: 'check_in'
      });
      return response.data
    }, () => null);
}

export function create(deptCode, details, sid, topics) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/create`, {deptCode, details, sid, topics}).then(response => {
      const appointmentId = response.data.id;
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} created an appointment`,
        action: 'check_in'
      });
      return response.data
    }, () => null);
}

export function getDropInAppointmentWaitlist(deptCode) {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/waitlist/${deptCode}`)
    .then(response => response.data, () => null);
}

export function getAllTopics() {
  return axios
    .get(`${utils.apiBaseUrl()}/api/appointments/topics`)
    .then(response => response.data, () => null);
}

export function markAppointmentRead(appointmentId) {
  return axios
    .post(`${utils.apiBaseUrl()}/api/appointments/${appointmentId}/mark_read`)
    .then(response => {
      store.dispatch('user/gaAppointmentEvent', {
        id: appointmentId,
        name: `Advisor ${store.getters['user/uid']} read an appointment`,
        action: 'read'
      });
      return response.data
    }, () => null);
}