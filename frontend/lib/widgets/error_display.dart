import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;

class ErrorDisplay extends StatelessWidget {
  final String errorId;
  final String message;
  final VoidCallback? onRetry;

  const ErrorDisplay({super.key, required this.errorId, required this.message, this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 400),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: Colors.red.shade50,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.red.shade200),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.error_outline_rounded, size: 48, color: Colors.red.shade400),
            const SizedBox(height: 16),
            Text(message, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () {
                Clipboard.setData(ClipboardData(text: errorId));
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('common.error_id_copied'.tr())));
              },
              child: Text('common.error_id'.tr(namedArgs: {'id': errorId}), style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: Text('common.retry'.tr()),
              ),
            ],
          ],
        ),
      ),
    );
  }

  static void showError(BuildContext context, String errorId, String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Row(
        children: [
          const Icon(Icons.error_outline, color: Colors.white, size: 20),
          const SizedBox(width: 8),
          Expanded(child: Text(message)),
          Text(errorId, style: const TextStyle(fontSize: 10, color: Colors.white70)),
        ],
      ),
      backgroundColor: Colors.red.shade700,
      duration: const Duration(seconds: 5),
      behavior: SnackBarBehavior.floating,
    ));
  }
}
