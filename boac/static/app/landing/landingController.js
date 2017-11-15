(function(angular) {

  'use strict';

  angular.module('boac').controller('LandingController', function(authService, cohortFactory, $rootScope, $scope) {

    $scope.isLoading = false;

    var loadTeams = function() {
      $scope.isLoading = true;

      cohortFactory.getTeams().then(function(teams) {
        $scope.teams = teams.data;
        $scope.isLoading = false;
      });
    };

    $rootScope.$on('authenticationFailure', function() {
      $scope.alertMessage = 'Log in failed. Please try again.';
    });

    authService.authWrap(loadTeams);
  });

}(window.angular));
