import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:medscribe_ai/services/notification_service.dart';

class NotificationBell extends ConsumerWidget {
  const NotificationBell({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final notifications = ref.watch(notificationProvider);
    final unread = notifications.where((n) => !n.isRead).length;

    return PopupMenuButton<String>(
      icon: Badge(
        isLabelVisible: unread > 0,
        label: Text('$unread'),
        child: const Icon(Icons.notifications),
      ),
      itemBuilder: (context) {
        if (notifications.isEmpty) {
          return [const PopupMenuItem(value: 'empty', child: Text('אין התראות'))];
        }
        return [
          PopupMenuItem(
            value: 'mark_all',
            child: const Text('סמן הכל כנקרא', style: TextStyle(color: Colors.blue, fontSize: 13)),
          ),
          ...notifications.take(10).map((n) => PopupMenuItem(
                value: n.id,
                child: ListTile(
                  dense: true,
                  leading: Icon(
                    n.type == 'error' ? Icons.error : Icons.check_circle,
                    color: n.type == 'error' ? Colors.red : Colors.green,
                    size: 20,
                  ),
                  title: Text(n.title, style: TextStyle(fontWeight: n.isRead ? FontWeight.normal : FontWeight.bold, fontSize: 13)),
                  subtitle: Text(n.message, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11)),
                ),
              )),
        ];
      },
      onSelected: (value) {
        if (value == 'mark_all') {
          ref.read(notificationProvider.notifier).markAllRead();
        } else if (value != 'empty') {
          ref.read(notificationProvider.notifier).markRead(value);
        }
      },
    );
  }
}
