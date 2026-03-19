import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';

enum TimerStatus { idle, running, paused, done }

class TimerState {
  final int totalSeconds;
  final int elapsedSeconds;
  final TimerStatus status;

  const TimerState({
    this.totalSeconds = 1200,
    this.elapsedSeconds = 0,
    this.status = TimerStatus.idle,
  });

  double get progress => totalSeconds > 0 ? elapsedSeconds / totalSeconds : 0;
  int get remainingSeconds => totalSeconds - elapsedSeconds;
  bool get isDone => status == TimerStatus.done;
  bool get isRunning => status == TimerStatus.running;
  bool get isPaused => status == TimerStatus.paused;
  bool get isIdle => status == TimerStatus.idle;

  String get remainingFormatted {
    final r = remainingSeconds.clamp(0, totalSeconds);
    return '${(r ~/ 60).toString().padLeft(2, '0')}:${(r % 60).toString().padLeft(2, '0')}';
  }

  String get elapsedFormatted {
    return '${(elapsedSeconds ~/ 60).toString().padLeft(2, '0')}:${(elapsedSeconds % 60).toString().padLeft(2, '0')}';
  }

  TimerState copyWith({int? totalSeconds, int? elapsedSeconds, TimerStatus? status}) =>
    TimerState(
      totalSeconds: totalSeconds ?? this.totalSeconds,
      elapsedSeconds: elapsedSeconds ?? this.elapsedSeconds,
      status: status ?? this.status,
    );
}

class TimerNotifier extends StateNotifier<TimerState> {
  Timer? _ticker;

  TimerNotifier() : super(const TimerState());

  void setDuration(int minutes) {
    if (state.isIdle) {
      state = state.copyWith(totalSeconds: minutes * 60);
    }
  }

  void start() {
    if (!state.isIdle && !state.isPaused) return;
    state = state.copyWith(status: TimerStatus.running);
    _startTicker();
  }

  void pause() {
    if (!state.isRunning) return;
    _ticker?.cancel();
    state = state.copyWith(status: TimerStatus.paused);
  }

  void resume() {
    if (!state.isPaused) return;
    state = state.copyWith(status: TimerStatus.running);
    _startTicker();
  }

  void reset() {
    _ticker?.cancel();
    state = state.copyWith(elapsedSeconds: 0, status: TimerStatus.idle);
  }

  void _startTicker() {
    _ticker?.cancel();
    _ticker = Timer.periodic(const Duration(seconds: 1), (_) {
      final next = state.elapsedSeconds + 1;
      if (next >= state.totalSeconds) {
        _ticker?.cancel();
        state = state.copyWith(elapsedSeconds: state.totalSeconds, status: TimerStatus.done);
      } else {
        state = state.copyWith(elapsedSeconds: next);
      }
    });
  }

  @override
  void dispose() {
    _ticker?.cancel();
    super.dispose();
  }
}

final timerProvider = StateNotifierProvider<TimerNotifier, TimerState>((ref) {
  return TimerNotifier();
});
