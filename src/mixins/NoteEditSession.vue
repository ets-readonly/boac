<script>
import _ from 'lodash';
import store from '@/store';
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'NoteEditSession',
  computed: {
    ...mapGetters('noteEditSession', [
      'addedCohorts',
      'addedCuratedGroups',
      'isFocusLockDisabled',
      'isSaving',
      'mode',
      'model',
      'noteTemplates',
      'sids',
      'targetStudentCount'
    ])
  },
  methods: {
    ...mapActions('noteEditSession', [
      'addAttachment',
      'addCohort',
      'addCuratedGroup',
      'addSid',
      'addTopic',
      'createAdvisingNote',
      'exitSession',
      'removeAttachment',
      'removeCohort',
      'removeCuratedGroup',
      'removeStudent',
      'removeTopic',
      'resetModel',
      'setBody',
      'setFocusLockDisabled',
      'setIsSaving',
      'setMode',
      'setModel',
      'setSubject'
    ]),
    setSubjectPerEvent(event) {
      store.dispatch('noteEditSession/setSubject', _.isString(event) ? event : event.target.value);
    }
  }
};
</script>
