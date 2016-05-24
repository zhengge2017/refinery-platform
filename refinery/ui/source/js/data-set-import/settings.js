'use strict';

angular
  .module('refineryDataSetImport')
  .constant('dataSetImportSettings', {
    checkFiles: '/data_set_manager/import/check_files/',
    isaTabImportUrl: '/data_set_manager/import/isa-tab-form/',
    tabularFileImportUrl: '/data_set_manager/import/metadata-table-form/',
    uploadUrl: '/data_set_manager/import/chunked-upload/',
    uploadCompleteUrl: '/data_set_manager/import/chunked-upload-complete/',
    chunkSize: 10 * 1024 * 1024  // 10 MB
  });
