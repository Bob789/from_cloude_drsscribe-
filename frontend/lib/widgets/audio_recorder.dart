import 'dart:async';
import 'dart:typed_data';
import 'dart:js_interop';
import 'package:flutter/material.dart';
import 'package:web/web.dart' as web;
import 'package:easy_localization/easy_localization.dart' hide TextDirection;

@JS('createVadHelper')
external _VadHelper _createVadHelper(JSObject stream);

extension type _VadHelper._(JSObject _) implements JSObject {
  external JSNumber getLevel();
  external void dispose();
}

const _chunkDurationSeconds = 5 * 60;
const _vadCheckMs = 60;
const _silenceTimeoutSec = 3;
const _vadThreshold = 0.025;
const _waveformBars = 32;

class AudioRecorder extends StatefulWidget {
  final void Function(Uint8List audioData, String mimeType, int chunkIndex, bool isFinal)? onChunkReady;
  final void Function(Uint8List audioData, String mimeType)? onRecordingComplete;

  const AudioRecorder({super.key, this.onChunkReady, this.onRecordingComplete});

  @override
  State<AudioRecorder> createState() => _AudioRecorderState();
}

class _AudioRecorderState extends State<AudioRecorder> {
  bool _isRecording = false;
  bool _isPaused = false;
  Duration _duration = Duration.zero;
  Timer? _timer;
  Timer? _chunkTimer;
  web.MediaRecorder? _mediaRecorder;
  web.MediaStream? _stream;
  final List<web.Blob> _currentChunks = [];
  int _chunkIndex = 0;
  int _chunksUploaded = 0;
  bool _stopping = false;

  _VadHelper? _vadHelper;
  Timer? _vadTimer;
  bool _vadEnabled = true;
  bool _vadAvailable = true;
  bool _isSpeaking = false;
  bool _autoPausedByVad = false;
  double _currentLevel = 0;
  final List<double> _waveformData = List.filled(_waveformBars, 0.0);
  int _silenceFrames = 0;
  Duration _speakingDuration = Duration.zero;

  int get _silenceFramesThreshold => _silenceTimeoutSec * 1000 ~/ _vadCheckMs;
  bool get _isChunkedMode => widget.onChunkReady != null;
  bool get _effectivelyPaused => _isPaused || _autoPausedByVad;

  Future<void> _startRecording() async {
    try {
      _stream = await web.window.navigator.mediaDevices
          .getUserMedia(web.MediaStreamConstraints(audio: true.toJS))
          .toDart;

      _chunkIndex = 0;
      _chunksUploaded = 0;
      _stopping = false;
      _speakingDuration = Duration.zero;
      _silenceFrames = 0;
      _isSpeaking = false;
      _autoPausedByVad = false;
      _waveformData.fillRange(0, _waveformBars, 0.0);

      _setupVad();
      _startMediaRecorder();

      setState(() {
        _isRecording = true;
        _isPaused = false;
        _duration = Duration.zero;
      });
      _startTimer();

      if (_isChunkedMode) {
        _chunkTimer = Timer.periodic(const Duration(seconds: _chunkDurationSeconds), (_) {
          if (_isRecording && !_isPaused && !_autoPausedByVad && !_stopping) {
            _rotateChunk();
          }
        });
      }
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('recording.mic_error'.tr(namedArgs: {'error': e.toString()}))));
    }
  }

  void _setupVad() {
    try {
      _vadHelper = _createVadHelper(_stream! as JSObject);
      _vadTimer = Timer.periodic(const Duration(milliseconds: _vadCheckMs), (_) => _checkVoiceActivity());
      _vadAvailable = true;
    } catch (_) {
      _vadAvailable = false;
      _vadEnabled = false;
    }
  }

  void _checkVoiceActivity() {
    if (_vadHelper == null || !_isRecording || _stopping || _isPaused) return;

    try {
      final level = _vadHelper!.getLevel().toDartDouble;
      final speaking = level > _vadThreshold;

      _waveformData.removeAt(0);
      _waveformData.add(level);

      if (speaking) {
        _silenceFrames = 0;
        if (_autoPausedByVad && _vadEnabled) {
          _autoPausedByVad = false;
          if (_mediaRecorder?.state == 'paused') {
            _mediaRecorder?.resume();
          }
        }
      } else {
        _silenceFrames++;
        if (_silenceFrames >= _silenceFramesThreshold &&
            _vadEnabled && !_autoPausedByVad &&
            _mediaRecorder?.state == 'recording') {
          _autoPausedByVad = true;
          _mediaRecorder?.pause();
        }
      }

      if (mounted) {
        setState(() {
          _currentLevel = level;
          _isSpeaking = speaking;
        });
      }
    } catch (_) {}
  }

  void _cleanupVad() {
    _vadTimer?.cancel();
    _vadTimer = null;
    try { _vadHelper?.dispose(); } catch (_) {}
    _vadHelper = null;
  }

  void _startMediaRecorder() {
    _currentChunks.clear();
    _mediaRecorder = web.MediaRecorder(_stream!, web.MediaRecorderOptions(mimeType: 'audio/webm;codecs=opus'));

    _mediaRecorder!.ondataavailable = (web.BlobEvent event) {
      if (event.data.size > 0) {
        _currentChunks.add(event.data);
      }
    }.toJS;

    _mediaRecorder!.onstop = (web.Event event) {
      final blob = web.Blob(_currentChunks.toJS);
      final reader = web.FileReader();
      final chunkIdx = _chunkIndex;
      final isFinal = _stopping;

      reader.readAsArrayBuffer(blob);
      reader.onloadend = (web.Event e) {
        final result = reader.result;
        if (result != null) {
          final bytes = (result as JSArrayBuffer).toDart.asUint8List();
          if (_isChunkedMode) {
            widget.onChunkReady!(bytes, 'audio/webm', chunkIdx, isFinal);
            if (!isFinal) {
              _chunksUploaded++;
              if (mounted) setState(() {});
            }
          } else {
            widget.onRecordingComplete?.call(bytes, 'audio/webm');
          }
        }
      }.toJS;
      _currentChunks.clear();

      if (!isFinal && _isRecording && !_stopping) {
        _chunkIndex++;
        _startMediaRecorder();
        _mediaRecorder!.start(1000);
        if (_autoPausedByVad) {
          _mediaRecorder?.pause();
        }
      }
    }.toJS;

    _mediaRecorder!.start(1000);
  }

  void _rotateChunk() {
    if (_mediaRecorder?.state == 'recording') {
      _mediaRecorder!.stop();
    }
  }

  void _pauseRecording() {
    if (_mediaRecorder?.state == 'recording') {
      _mediaRecorder?.pause();
    }
    _timer?.cancel();
    _autoPausedByVad = false;
    setState(() => _isPaused = true);
  }

  void _resumeRecording() {
    if (_mediaRecorder?.state == 'paused') {
      _mediaRecorder?.resume();
    }
    _autoPausedByVad = false;
    _silenceFrames = 0;
    if (_isPaused) _startTimer();
    setState(() => _isPaused = false);
  }

  void _stopRecording() {
    _stopping = true;
    _chunkTimer?.cancel();
    _chunkTimer = null;
    _cleanupVad();

    if (_mediaRecorder?.state == 'recording' || _mediaRecorder?.state == 'paused') {
      _mediaRecorder!.stop();
    }

    _stream?.getTracks().toDart.forEach((track) => track.stop());
    _timer?.cancel();
    setState(() {
      _isRecording = false;
      _isPaused = false;
      _autoPausedByVad = false;
    });
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      setState(() {
        _duration += const Duration(seconds: 1);
        if (_isSpeaking && !_autoPausedByVad) {
          _speakingDuration += const Duration(seconds: 1);
        }
      });
    });
  }

  String _formatDuration(Duration d) {
    final minutes = d.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds = d.inSeconds.remainder(60).toString().padLeft(2, '0');
    final hours = d.inHours.toString().padLeft(2, '0');
    return '$hours:$minutes:$seconds';
  }

  @override
  void dispose() {
    _timer?.cancel();
    _chunkTimer?.cancel();
    _cleanupVad();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Stack(
              alignment: Alignment.center,
              children: [
                if (_isRecording && _isSpeaking)
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 80 + _currentLevel * 30,
                    height: 80 + _currentLevel * 30,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: Colors.red.withValues(alpha: 0.06 + _currentLevel * 0.12),
                    ),
                  ),
                Icon(
                  _isRecording ? Icons.mic : Icons.mic_none,
                  size: 64,
                  color: _isRecording
                      ? (_autoPausedByVad ? Colors.orange : Colors.red)
                      : Colors.grey,
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              _formatDuration(_duration),
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontFamily: 'monospace'),
            ),
            if (_isRecording && _vadEnabled && _vadAvailable) ...[
              const SizedBox(height: 2),
              Text(
                'recording.speaking_duration'.tr(namedArgs: {'duration': _formatDuration(_speakingDuration)}),
                style: TextStyle(fontSize: 13, color: Colors.grey.shade600, fontFamily: 'monospace'),
              ),
            ],
            const SizedBox(height: 8),
            if (_isRecording) ...[
              _buildWaveform(),
              const SizedBox(height: 8),
              if (_vadEnabled && _vadAvailable) _buildVadStatus(),
            ],
            if (_isRecording && _isChunkedMode) ...[
              const SizedBox(height: 8),
              _buildChunkStatus(),
            ],
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                if (!_isRecording)
                  FloatingActionButton.large(
                    onPressed: _startRecording,
                    backgroundColor: Colors.red,
                    child: const Icon(Icons.mic, color: Colors.white, size: 36),
                  )
                else ...[
                  IconButton.filled(
                    onPressed: _effectivelyPaused ? _resumeRecording : _pauseRecording,
                    icon: Icon(_effectivelyPaused ? Icons.play_arrow : Icons.pause),
                  ),
                  const SizedBox(width: 24),
                  FloatingActionButton(
                    onPressed: _stopRecording,
                    backgroundColor: Colors.red,
                    child: const Icon(Icons.stop, color: Colors.white),
                  ),
                ],
              ],
            ),
            if (_isRecording && _vadAvailable) ...[
              const SizedBox(height: 16),
              _buildVadToggle(),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildVadStatus() {
    if (_autoPausedByVad) {
      return Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.pause_circle_outline, size: 14, color: Colors.orange.shade600),
          const SizedBox(width: 6),
          Text(
            'recording.silence_waiting'.tr(),
            style: TextStyle(fontSize: 12, color: Colors.orange.shade600, fontWeight: FontWeight.w500),
          ),
        ],
      );
    }
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: _isSpeaking ? Colors.green : Colors.grey.shade400,
          ),
        ),
        const SizedBox(width: 6),
        Text(
          _isSpeaking ? 'recording.speech_detected'.tr() : 'recording.silence'.tr(),
          style: TextStyle(
            fontSize: 12,
            color: _isSpeaking ? Colors.green.shade700 : Colors.grey.shade500,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _buildVadToggle() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(Icons.graphic_eq_rounded, size: 16, color: _vadEnabled ? Colors.blue.shade600 : Colors.grey.shade400),
        const SizedBox(width: 6),
        Text('recording.voice_detection'.tr(), style: TextStyle(fontSize: 12, color: Colors.grey.shade600)),
        const SizedBox(width: 8),
        SizedBox(
          height: 24,
          child: Switch(
            value: _vadEnabled,
            onChanged: (v) {
              setState(() {
                _vadEnabled = v;
                if (!v && _autoPausedByVad) {
                  _autoPausedByVad = false;
                  if (_mediaRecorder?.state == 'paused') {
                    _mediaRecorder?.resume();
                  }
                }
              });
            },
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
        ),
      ],
    );
  }

  Widget _buildWaveform() {
    return SizedBox(
      height: 48,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: List.generate(_waveformBars, (i) {
          final level = _waveformData[i];
          final normalizedHeight = _effectivelyPaused
              ? 3.0
              : (3.0 + level * 45.0).clamp(3.0, 48.0);

          Color barColor;
          if (_isPaused) {
            barColor = Colors.grey.shade300;
          } else if (_autoPausedByVad) {
            barColor = Colors.orange.withValues(alpha: 0.3);
          } else if (_isSpeaking) {
            barColor = Colors.red.withValues(alpha: 0.5 + level * 0.5);
          } else {
            barColor = Colors.grey.withValues(alpha: 0.3 + level * 0.4);
          }

          return AnimatedContainer(
            duration: const Duration(milliseconds: 80),
            width: 3,
            height: normalizedHeight,
            margin: const EdgeInsets.symmetric(horizontal: 1),
            decoration: BoxDecoration(
              color: barColor,
              borderRadius: BorderRadius.circular(2),
            ),
          );
        }),
      ),
    );
  }

  Widget _buildChunkStatus() {
    final currentChunk = _chunkIndex + 1;
    final timeInChunk = _duration.inSeconds % _chunkDurationSeconds;
    final chunkProgress = timeInChunk / _chunkDurationSeconds;

    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.cloud_upload_rounded, size: 14, color: Colors.green.shade600),
            const SizedBox(width: 4),
            Text(
              'recording.chunks_uploaded'.tr(namedArgs: {'count': _chunksUploaded.toString()}),
              style: TextStyle(fontSize: 12, color: Colors.green.shade600, fontWeight: FontWeight.w600),
            ),
            const SizedBox(width: 12),
            Text(
              'recording.current_chunk'.tr(namedArgs: {'count': currentChunk.toString()}),
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: chunkProgress,
            minHeight: 3,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation<Color>(Colors.red.shade300),
          ),
        ),
      ],
    );
  }
}
