import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:medscribe_ai/services/api_client.dart';

class TranscriptionScreen extends ConsumerStatefulWidget {
  final String transcriptionId;
  const TranscriptionScreen({super.key, required this.transcriptionId});

  @override
  ConsumerState<TranscriptionScreen> createState() => _TranscriptionScreenState();
}

class _TranscriptionScreenState extends ConsumerState<TranscriptionScreen> {
  Map<String, dynamic>? _data;
  bool _isLoading = true;
  bool _isEditing = false;
  final _textController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final response = await ApiClient().dio.get('/transcriptions/${widget.transcriptionId}');
      setState(() {
        _data = response.data;
        _textController.text = _data?['full_text'] ?? '';
        _isLoading = false;
      });
    } catch (_) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _save() async {
    try {
      await ApiClient().dio.put('/transcriptions/${widget.transcriptionId}', data: {'full_text': _textController.text});
      setState(() => _isEditing = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('common.saved_success'.tr())));
    } catch (_) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('common.save_error'.tr())));
    }
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_data == null) return Center(child: Text('transcription.not_found'.tr()));

    final speakers = _data!['speakers_json'] as List? ?? [];
    final status = _data!['status'];

    return Scaffold(
      appBar: AppBar(
        title: Text('transcription.title'.tr()),
        actions: [
          if (status == 'done')
            IconButton(
              icon: Icon(_isEditing ? Icons.save : Icons.edit),
              onPressed: _isEditing ? _save : () => setState(() => _isEditing = true),
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(MediaQuery.of(context).size.width < 500 ? 12 : 24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildStatusChip(status),
            const SizedBox(height: 16),
            if (_data!['confidence_score'] != null)
              Text('${'summary.accuracy'.tr()}: ${(_data!['confidence_score'] * 100).toStringAsFixed(1)}%'),
            const SizedBox(height: 16),
            if (_isEditing)
              TextField(
                controller: _textController,
                maxLines: null,
                decoration: InputDecoration(border: OutlineInputBorder(), labelText: 'transcription.text_label'.tr()),
              )
            else if (speakers.isNotEmpty)
              ...speakers.map((seg) => _buildSegment(seg))
            else
              SelectableText(_data!['full_text'] ?? '', style: const TextStyle(fontSize: 16, height: 1.6)),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    final colors = {'pending': Colors.grey, 'processing': Colors.orange, 'done': Colors.green, 'error': Colors.red};
    final labels = {
      'pending': 'transcription.status_pending'.tr(),
      'processing': 'transcription.status_processing'.tr(),
      'done': 'transcription.status_done'.tr(),
      'error': 'transcription.status_error'.tr(),
    };
    return Chip(
      label: Text(labels[status] ?? status),
      backgroundColor: (colors[status] ?? Colors.grey).withValues(alpha: 0.2),
    );
  }

  Widget _buildSegment(Map<String, dynamic> seg) {
    final speaker = seg['speaker'] ?? 'unknown';
    final isDoctor = speaker == 'doctor';
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDoctor ? Colors.blue.withValues(alpha: 0.1) : Colors.green.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border(right: BorderSide(color: isDoctor ? Colors.blue : Colors.green, width: 3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isDoctor ? 'transcription.speaker_doctor'.tr() : (speaker == 'patient' ? 'transcription.speaker_patient'.tr() : 'transcription.speaker_unknown'.tr()),
            style: TextStyle(fontWeight: FontWeight.bold, color: isDoctor ? Colors.blue : Colors.green, fontSize: 12),
          ),
          const SizedBox(height: 4),
          Text(seg['text'] ?? '', style: const TextStyle(fontSize: 15, height: 1.5)),
        ],
      ),
    );
  }
}
