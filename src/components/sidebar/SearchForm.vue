<template>
  <div class="sidebar-section-search">
    <form
      id="search-students-form"
      autocomplete="off"
      :class="{'search-students-page-body': context === 'pageBody'}"
      @submit.prevent="search()">
      <div v-if="context === 'sidebar'" class="search-students-form-label-outer search-label">
        <div>
          <i class="fas fa-search"></i>
          <label
            for="search-students-input"
            class="search-students-form-label">Search</label>
        </div>
        <b-btn
          id="search-options-panel-toggle"
          v-b-toggle="'search-options-panel'"
          class="search-options-panel-toggle"
          variant="link">
          <span class="when-options-panel-closed">Show options</span>
          <span class="when-options-panel-open">Hide options</span>
        </b-btn>
      </div>
      <div :class="{'search-students-form-button': context === 'pageBody'}">
        <input
          id="search-students-input"
          v-model="searchPhrase"
          class="search-students-input"
          :readonly="disable"
          type="text"
          maxlength="255" />
      </div>
      <div v-if="context === 'pageBody'">
        <b-btn
          id="search-students-button"
          variant="primary"
          class="btn-search-students btn-primary-color-override"
          type="submit">
          Search
        </b-btn>
      </div>
      <b-collapse
        v-if="context === 'sidebar'"
        id="search-options-panel"
        class="search-students-form-label-outer">
        <div>
          <b-form-checkbox
            id="search-include-students-checkbox"
            v-model="includeStudents"
            plain>
          </b-form-checkbox>
          <label
            for="search-include-students-checkbox"
            class="search-students-form-label">
            <span class="sr-only">Search for</span>
            Students (name or SID)
          </label>
        </div>
        <div>
          <b-form-checkbox
            id="search-include-courses-checkbox"
            v-model="includeCourses"
            plain>
          </b-form-checkbox>
          <label
            for="search-include-courses-checkbox"
            class="search-students-form-label">
            <span class="sr-only">Search for</span>
            Classes
          </label>
        </div>
        <div>
          <b-form-checkbox
            id="search-include-notes-checkbox"
            v-model="includeNotes"
            plain>
          </b-form-checkbox>
          <label
            for="search-include-notes-checkbox"
            class="search-students-form-label">
            <span class="sr-only">Search for</span>
            Notes
          </label>
        </div>
      </b-collapse>
    </form>
  </div>
</template>

<script>
import GoogleAnalytics from '@/mixins/GoogleAnalytics';
import Util from '@/mixins/Util';

export default {
  name: 'SearchForm',
  mixins: [GoogleAnalytics, Util],
  props: {
    context: String,
    domain: Array,
  },
  data() {
    return {
      disable: false,
      includeCourses: this.domain.includes('courses'),
      includeNotes: this.domain.includes('notes'),
      includeStudents: this.domain.includes('students'),
      searchPhrase: null
    };
  },
  methods: {
    search() {
      this.searchPhrase = this.trim(this.searchPhrase);
      if (this.searchPhrase) {
        this.$router.push({
          path: this.forceUniquePath('/search'),
          query: {
            q: this.searchPhrase,
            courses: this.includeCourses,
            notes: this.includeNotes,
            students: this.includeStudents,
          }
        });
        this.gaEvent(
          'Search',
          'submit',
          this.includeCourses ? 'classes and students' : 'students',
          this.searchPhrase
        );
      }
    }
  }
};
</script>

<style scoped>
.btn-search-students {
  height: 46px;
}
.collapsed > .when-options-panel-open,
:not(.collapsed) > .when-options-panel-closed {
  display: none;
}
.search-label {
  display: flex;
  align-items: baseline;
  font-size: 14px;
}
.search-label i {
  padding-right: 4px;
}
.search-options-panel-toggle {
  color: #8bbdda;
  font-size: 12px;
  padding: 0;
}
.search-students-form-button {
  min-width: 200px;
  width: 60%;
}
.search-students-form-label {
  font-weight: 400;
  margin: 0;
}
.search-students-form-label-outer {
  color: #fff;
  justify-content: space-between;
  margin: 10px 0;
}
.search-students-input {
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 4px;
  color: #333;
  padding: 10px;
  width: 100%;
}
.search-students-page-body {
  align-items: center;
  display: flex;
  flex-flow: row wrap;
  margin-top: 10px;
}
.search-students-page-body div {
  align-self: flex-end;
}
.search-students-page-body div:first-child {
  padding-right: 15px;
}
.sidebar-section-search {
  margin: 0 12px 12px 12px;
}
</style>