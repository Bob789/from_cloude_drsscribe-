import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class AppNotification {
  final String id;
  final String title;
  final String message;
  final String type;
  final DateTime createdAt;
  bool isRead;

  AppNotification({
    required this.id,
    required this.title,
    required this.message,
    this.type = 'info',
    this.isRead = false,
  }) : createdAt = DateTime.now();
}

class NotificationService extends StateNotifier<List<AppNotification>> {
  NotificationService() : super([]);

  int get unreadCount => state.where((n) => !n.isRead).length;

  void add(String title, String message, {String type = 'info'}) {
    state = [
      AppNotification(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        title: title,
        message: message,
        type: type,
      ),
      ...state,
    ].take(50).toList();
  }

  void markRead(String id) {
    state = state.map((n) {
      if (n.id == id) n.isRead = true;
      return n;
    }).toList();
  }

  void markAllRead() {
    state = state.map((n) {
      n.isRead = true;
      return n;
    }).toList();
  }

  void clear() {
    state = [];
  }
}

final notificationProvider = StateNotifierProvider<NotificationService, List<AppNotification>>((ref) {
  return NotificationService();
});
