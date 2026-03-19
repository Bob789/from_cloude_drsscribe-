import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;

class ErrorScreen extends StatelessWidget {
  final String? message;
  const ErrorScreen({super.key, this.message});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 80, color: Colors.red),
            const SizedBox(height: 16),
            Text('error.server_error'.tr(), style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text(message ?? 'error.unexpected'.tr(), style: TextStyle(color: Colors.grey[600])),
            const SizedBox(height: 24),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                ElevatedButton(onPressed: () => context.go('/dashboard'), child: Text('error.back_home'.tr())),
                const SizedBox(width: 12),
                OutlinedButton(onPressed: () {}, child: Text('common.retry'.tr())),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
