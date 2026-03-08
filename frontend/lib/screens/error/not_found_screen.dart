import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;

class NotFoundScreen extends StatelessWidget {
  const NotFoundScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.search_off, size: 80, color: Colors.grey),
            const SizedBox(height: 16),
            Text('404', style: Theme.of(context).textTheme.displayLarge?.copyWith(color: Colors.grey)),
            const SizedBox(height: 8),
            Text('error.not_found'.tr()),
            const SizedBox(height: 24),
            ElevatedButton(onPressed: () => context.go('/dashboard'), child: Text('error.back_to_dashboard'.tr())),
          ],
        ),
      ),
    );
  }
}
