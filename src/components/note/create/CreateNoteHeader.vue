<template>
  <div class="align-items-end d-flex flex-wrap mb-1 mt-2 pt-2">
    <div class="flex-grow-1 new-note-header font-weight-bolder">
      <span v-if="mode === 'editTemplate'">Edit Template</span>
      <span v-if="mode !== 'editTemplate'">New Note</span>
    </div>
    <div class="mr-4">
      <b-dropdown
        v-if="mode !== 'editTemplate'"
        id="my-templates-button"
        :disabled="isSaving"
        text="Templates"
        aria-label="Select a note template"
        variant="primary"
        class="mb-2 ml-0"
        right>
        <b-dropdown-header v-if="!size(noteTemplates)" id="no-templates-header" class="templates-dropdown-header">
          <div class="font-weight-bolder">Templates</div>
          <div class="templates-dropdown-instructions">
            You have no saved templates.
          </div>
        </b-dropdown-header>
        <b-dropdown-text
          v-for="template in noteTemplates"
          :key="template.id">
          <div class="align-items-center d-flex font-weight-normal justify-content-between text-nowrap">
            <b-link
              :id="`load-note-template-${template.id}`"
              :title="template.title"
              class="pb-0 text-nowrap template-dropdown-title truncate-with-ellipsis"
              @click="loadTemplate(template)">
              {{ template.title }}
            </b-link>
            <div class="align-items-center d-flex ml-3">
              <div class="pl-2">
                <b-btn
                  :id="`btn-rename-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="openRenameTemplateModal(template)">
                  Rename<span class="sr-only"> template {{ template.title }}</span>
                </b-btn>
              </div>
              <div class="pl-1 pr-1">
                |
              </div>
              <div>
                <b-btn
                  :id="`btn-edit-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="editTemplate(template)">
                  Edit<span class="sr-only"> template {{ template.title }}</span>
                </b-btn>
              </div>
              <div class="pl-1 pr-1">
                |
              </div>
              <div>
                <b-btn
                  :id="`btn-delete-note-template-${template.id}`"
                  variant="link"
                  class="p-0"
                  @click="openDeleteTemplateModal(template)">
                  Delete<span class="sr-only"> template {{ template.title }}</span>
                </b-btn>
              </div>
            </div>
          </div>
        </b-dropdown-text>
      </b-dropdown>
    </div>
    <RenameTemplateModal
      v-if="showRenameTemplateModal"
      :show-modal="showRenameTemplateModal"
      :cancel="cancel"
      :rename="renameTemplate"
      :template="targetTemplate"
      :toggle-show="toggleShowRenameTemplateModal" />
    <AreYouSureModal
      v-if="showDeleteTemplateModal"
      :function-cancel="cancel"
      :function-confirm="deleteTemplateConfirmed"
      :modal-body="`Are you sure you want to delete the <b>'${get(targetTemplate, 'title')}'</b> template?`"
      :show-modal="showDeleteTemplateModal"
      button-label-confirm="Delete"
      modal-header="Delete Template" />
  </div>
</template>

<script>
import AreYouSureModal from '@/components/util/AreYouSureModal';
import Context from '@/mixins/Context';
import NoteEditSession from '@/mixins/NoteEditSession';
import RenameTemplateModal from '@/components/note/create/RenameTemplateModal';
import Util from '@/mixins/Util';
import {deleteNoteTemplate, renameNoteTemplate} from '@/api/note-templates';

export default {
  name: 'CreateNoteHeader',
  components: {AreYouSureModal, RenameTemplateModal},
  mixins: [Context, NoteEditSession, Util],
  props: {
    cancelPrimaryModal: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    showDeleteTemplateModal: false,
    showRenameTemplateModal: false,
    targetTemplate: undefined
  }),
  methods: {
    cancel() {
      this.showDeleteTemplateModal = false;
      this.showRenameTemplateModal = false;
      this.targetTemplate = null;
      this.putFocusNextTick('create-note-subject');
      this.setFocusLockDisabled(false);
    },
    deleteTemplateConfirmed() {
      deleteNoteTemplate(this.targetTemplate.id).then(() => {
        this.showDeleteTemplateModal = false;
        this.setFocusLockDisabled(false);
        this.targetTemplate = null;
        this.putFocusNextTick('create-note-subject');
      })
    },
    editTemplate(template) {
      this.setModel(this.cloneDeep(template));
      this.setMode('editTemplate');
      this.putFocusNextTick('create-note-subject');
    },
    loadTemplate(template) {
      this.setModel(this.cloneDeep(template));
      this.putFocusNextTick('create-note-subject');
      this.alertScreenReader(`Template ${template.title} loaded`);
    },
    openDeleteTemplateModal(template) {
      this.targetTemplate = template;
      this.setFocusLockDisabled(true);
      this.showDeleteTemplateModal = true;
    },
    openRenameTemplateModal(template) {
      this.targetTemplate = template;
      this.setFocusLockDisabled(true);
      this.showRenameTemplateModal = true;
    },
    renameTemplate(title) {
      renameNoteTemplate(this.targetTemplate.id, title).then(() => {
        this.targetTemplate = null;
        this.showRenameTemplateModal = false;
        this.setFocusLockDisabled(false);
      });
    },
    toggleShowRenameTemplateModal(show) {
      this.showRenameTemplateModal = show;
      this.setFocusLockDisabled(show);
    }
  }
}
</script>

<style scoped>
.new-note-header {
  font-size: 24px;
  margin: 0 15px 6px 15px;
}
.template-dropdown-title {
  max-width: 200px;
}
.templates-dropdown-header {
  width: 300px;
}
.templates-dropdown-instructions {
  max-width: 300px;
  white-space: normal;
}
</style>
