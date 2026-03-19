import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;

class SessionExpiredScreen extends StatelessWidget {
  const SessionExpiredScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.lock_clock, size: 80, color: Colors.orange),
            const SizedBox(height: 16),
            Text('error.session_expired'.tr(), style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text('error.please_login_again'.tr()),
            const SizedBox(height: 24),
            ElevatedButton(onPressed: () => context.go('/login'), child: Text('error.login_again'.tr())),
          ],
        ),
      ),
    );
  }
}
