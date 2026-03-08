class ApiEndpoints {
  static const patients = '/patients';
  static String patientById(String id) => '/patients/$id';
  static const patientSearch = '/patients/search';

  static const visits = '/visits';
  static const visitManual = '/visits/manual';
  static String visitPatient(String id) => '/visits/patient/$id';
  static String visitById(String id) => '/visits/$id';
  static String visitComplete(String id) => '/visits/$id/complete';

  static const recordingUpload = '/recordings/upload';
  static const recordingChunk = '/recordings/upload-chunk';
  static String recordingFinalize(String id) => '/recordings/finalize/$id';

  static const summaries = '/summaries';
  static String summaryGenerate(String id) => '/summaries/generate/$id';
  static String summaryByVisit(String id) => '/summaries/visit/$id';

  static const search = '/search';
  static const searchReindex = '/search/reindex';

  static const tags = '/tags';
  static String tagById(String id) => '/tags/$id';

  static const customFields = '/custom-fields';
  static String customFieldById(int id) => '/custom-fields/$id';

  static const dashboardStats = '/dashboard/stats';

  static const authGoogle = '/auth/google';
  static const authRefresh = '/auth/refresh';
  static const authMe = '/auth/me';

  static String patientFiles(String id) => '/patients/$id/files';
  static String patientFileUpload(String id) => '/patients/$id/files/upload';
  static String patientFileUploadMultiple(String id) => '/patients/$id/files/upload-multiple';

  static const adminUsers = '/admin/users';
  static const adminAudit = '/admin/audit';
  static const adminClinics = '/admin/clinics';

  static const reportsUsage = '/reports/usage';
  static const reportsDoctors = '/reports/doctors';
}
