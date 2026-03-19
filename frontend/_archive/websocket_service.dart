import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final _statusController = StreamController<Map<String, dynamic>>.broadcast();
  Timer? _pingTimer;

  Stream<Map<String, dynamic>> get statusStream => _statusController.stream;

  void connect(String visitId) {
    final uri = Uri.parse('ws://${Uri.base.host}/ws/visits/$visitId/status');
    _channel = WebSocketChannel.connect(uri);

    _channel!.stream.listen(
      (data) {
        try {
          final message = jsonDecode(data);
          if (message['type'] != 'pong') {
            _statusController.add(message);
          }
        } catch (_) {}
      },
      onDone: () => _reconnect(visitId),
      onError: (_) => _reconnect(visitId),
    );

    _pingTimer = Timer.periodic(const Duration(seconds: 30), (_) {
      _channel?.sink.add('ping');
    });
  }

  void _reconnect(String visitId) {
    _pingTimer?.cancel();
    Future.delayed(const Duration(seconds: 3), () => connect(visitId));
  }

  void disconnect() {
    _pingTimer?.cancel();
    _channel?.sink.close();
  }

  void dispose() {
    disconnect();
    _statusController.close();
  }
}
