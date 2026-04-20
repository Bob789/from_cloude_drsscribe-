import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:medscribe_ai/providers/auth_provider.dart';
import 'package:medscribe_ai/screens/login_screen.dart';
import 'package:medscribe_ai/screens/dashboard_screen.dart';
import 'package:medscribe_ai/screens/patients_screen.dart';
import 'package:medscribe_ai/screens/patient_profile_screen.dart';
import 'package:medscribe_ai/screens/patient_form_screen.dart';
import 'package:medscribe_ai/screens/recording_screen.dart';
import 'package:medscribe_ai/screens/search_screen.dart';
import 'package:medscribe_ai/screens/settings_screen.dart';
import 'package:medscribe_ai/screens/admin/users_screen.dart';
import 'package:medscribe_ai/screens/admin/audit_screen.dart';
import 'package:medscribe_ai/screens/admin/activity_screen.dart';
import 'package:medscribe_ai/screens/admin/reports_screen.dart';
import 'package:medscribe_ai/screens/admin/dev_tools_screen.dart';
import 'package:medscribe_ai/screens/manual_note_screen.dart';
import 'package:medscribe_ai/screens/question_templates_screen.dart';
import 'package:medscribe_ai/screens/appointments_screen.dart';
import 'package:medscribe_ai/screens/help/help_screen.dart';
import 'package:medscribe_ai/screens/help/help_detail_screen.dart';
import 'package:medscribe_ai/screens/error/not_found_screen.dart';
import 'package:medscribe_ai/widgets/app_shell.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authProvider);

  return GoRouter(
    initialLocation: '/login',
    errorBuilder: (context, state) => const NotFoundScreen(),
    redirect: (context, state) {
      final isAuth = authState.status == AuthStatus.authenticated;
      final isLoginRoute = state.matchedLocation == '/login';

      if (!isAuth && !isLoginRoute) return '/login';
      if (isAuth && isLoginRoute) return '/dashboard';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      ShellRoute(
        builder: (context, state, child) => AppShell(child: child),
        routes: [
          GoRoute(
              path: '/dashboard',
              builder: (context, state) => const DashboardScreen()),
          GoRoute(
              path: '/patients',
              builder: (context, state) => const PatientsScreen()),
          GoRoute(
              path: '/patients/new',
              builder: (context, state) => const PatientFormScreen()),
          GoRoute(
              path: '/patients/:id',
              builder: (context, state) =>
                  PatientProfileScreen(patientId: state.pathParameters['id']!)),
          GoRoute(
              path: '/patients/:id/edit',
              builder: (context, state) =>
                  PatientFormScreen(patientId: state.pathParameters['id'])),
          GoRoute(
              path: '/recording',
              builder: (context, state) => const RecordingScreen()),
          GoRoute(
              path: '/manual-note',
              builder: (context, state) => const ManualNoteScreen()),
          GoRoute(
              path: '/question-templates',
              builder: (context, state) => const QuestionTemplatesScreen()),
          GoRoute(
              path: '/appointments',
              builder: (context, state) => const AppointmentsScreen()),
          GoRoute(
              path: '/search',
              builder: (context, state) => const SearchScreen()),
          GoRoute(
              path: '/settings',
              builder: (context, state) => const SettingsScreen()),
          GoRoute(
              path: '/help', builder: (context, state) => const HelpScreen()),
          GoRoute(
              path: '/help/:category',
              builder: (context, state) => HelpDetailScreen(
                  category: state.pathParameters['category']!)),
          GoRoute(
              path: '/admin',
              builder: (context, state) => const AdminUsersScreen()),
          GoRoute(
              path: '/admin/audit',
              builder: (context, state) => const AuditScreen()),
          GoRoute(
              path: '/admin/activity',
              builder: (context, state) => const ActivityScreen()),
          GoRoute(
              path: '/admin/reports',
              builder: (context, state) => const ReportsScreen()),
          GoRoute(
              path: '/admin/dev-tools',
              builder: (context, state) => const DevToolsScreen()),
        ],
      ),
    ],
  );
});
