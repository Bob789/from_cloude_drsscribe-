import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:easy_localization/easy_localization.dart' hide TextDirection;
import 'package:intl/intl.dart';
import 'package:medscribe_ai/models/appointment_model.dart';
import 'package:medscribe_ai/providers/appointments_provider.dart';
import 'package:medscribe_ai/services/api_client.dart';
import 'package:medscribe_ai/utils/app_theme.dart';
import 'package:medscribe_ai/utils/themes/medscribe_theme_extension.dart';

class AppointmentsScreen extends ConsumerStatefulWidget {
  const AppointmentsScreen({super.key});

  @override
  ConsumerState<AppointmentsScreen> createState() => _AppointmentsScreenState();
}

class _AppointmentsScreenState extends ConsumerState<AppointmentsScreen> {

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(appointmentsProvider);
    final ext = Theme.of(context).extension<MedScribeThemeExtension>()!;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: state.isLoading
          ? Center(child: CircularProgressIndicator(color: AppColors.primary, strokeWidth: 2.5))
          : Padding(
              padding: const EdgeInsets.all(24),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                _buildHeader(state),
                const SizedBox(height: 20),
                if (state.viewMode == CalendarViewMode.weekly) ...[
                  _buildWeekNav(state, ext),
                  const SizedBox(height: 16),
                  _buildWeekGrid(state, ext),
                ] else ...[
                  _buildMonthNav(state, ext),
                  const SizedBox(height: 16),
                  _buildMonthGrid(state, ext),
                ],
                const SizedBox(height: 20),
                Expanded(child: _buildDayDetail(state, ext)),
              ]),
            ),
    );
  }

  // ── Header + Toggle ──

  Widget _buildHeader(AppointmentsState state) {
    final notifier = ref.read(appointmentsProvider.notifier);
    return Row(children: [
      Text('appointments.title'.tr(), style: GoogleFonts.heebo(fontSize: 26, fontWeight: FontWeight.w800, color: AppColors.textPrimary)),
      const SizedBox(width: 24),
      _buildViewToggle(state, notifier),
      const Spacer(),
      _buildCalendarStatus(state),
      const SizedBox(width: 12),
      ElevatedButton.icon(
        onPressed: () => _showCreateDialog(),
        icon: const Icon(Icons.add, size: 18),
        label: Text('appointments.new_appointment'.tr(), style: GoogleFonts.heebo(fontWeight: FontWeight.w600)),
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
    ]);
  }

  Widget _buildViewToggle(AppointmentsState state, AppointmentsNotifier notifier) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.background,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.cardBorder),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        _toggleButton('appointments.weekly'.tr(), Icons.view_week_rounded, state.viewMode == CalendarViewMode.weekly, () => notifier.setViewMode(CalendarViewMode.weekly)),
        _toggleButton('appointments.monthly'.tr(), Icons.calendar_view_month_rounded, state.viewMode == CalendarViewMode.monthly, () => notifier.setViewMode(CalendarViewMode.monthly)),
      ]),
    );
  }

  Widget _toggleButton(String label, IconData icon, bool isActive, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isActive ? AppColors.primary : Colors.transparent,
          borderRadius: BorderRadius.circular(9),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(icon, size: 16, color: isActive ? Colors.white : AppColors.textMuted),
          const SizedBox(width: 6),
          Text(label, style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: isActive ? Colors.white : AppColors.textMuted)),
        ]),
      ),
    );
  }

  Widget _buildCalendarStatus(AppointmentsState state) {
    if (state.calendarConnected) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(color: AppColors.success.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(8)),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.check_circle, size: 16, color: AppColors.success),
          const SizedBox(width: 6),
          Text('appointments.calendar_connected'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.success)),
        ]),
      );
    }
    return OutlinedButton.icon(
      onPressed: _connectCalendar,
      icon: const Icon(Icons.link, size: 16),
      label: Text('appointments.connect_calendar'.tr(), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w500)),
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.textSecondary,
        side: BorderSide(color: AppColors.cardBorder),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  // ── Weekly View (unchanged) ──

  Widget _buildWeekNav(AppointmentsState state, MedScribeThemeExtension ext) {
    final ws = state.weekStart;
    final we = ws.add(const Duration(days: 6));
    final label = '${ws.day}-${we.day} ${DateFormat('MMMM', context.locale.toString()).format(ws)} ${ws.year}';
    final notifier = ref.read(appointmentsProvider.notifier);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: ext.cardDecoration,
      child: Row(children: [
        IconButton(icon: const Icon(Icons.chevron_right), onPressed: notifier.previousWeek, iconSize: 20, color: AppColors.textSecondary),
        const Spacer(),
        Text(label, style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const Spacer(),
        IconButton(icon: const Icon(Icons.chevron_left), onPressed: notifier.nextWeek, iconSize: 20, color: AppColors.textSecondary),
      ]),
    );
  }

  Widget _buildWeekGrid(AppointmentsState state, MedScribeThemeExtension ext) {
    return Row(
      children: List.generate(7, (i) {
        final day = state.weekStart.add(Duration(days: i));
        final isSelected = _sameDay(day, state.selectedDate);
        final isToday = _sameDay(day, DateTime.now());
        final dayAppts = state.appointments.where((a) => _sameDay(a.startTime, day)).toList();
        final holiday = state.holidays.where((h) => h.date == _fmt(day)).toList();

        return Expanded(
          child: GestureDetector(
            onTap: () => ref.read(appointmentsProvider.notifier).selectDate(day),
            child: Container(
              margin: EdgeInsets.only(left: i > 0 ? 8 : 0),
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
              decoration: BoxDecoration(
                color: isSelected ? AppColors.primary.withValues(alpha: 0.15) : null,
                border: isToday ? Border.all(color: AppColors.primary, width: 2) : Border.all(color: AppColors.cardBorder),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                Text(DateFormat('E', context.locale.toString()).format(day).substring(0, 2), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: isSelected ? AppColors.primary : AppColors.textSecondary)),
                const SizedBox(height: 4),
                Text('${day.day}', style: GoogleFonts.heebo(fontSize: 18, fontWeight: FontWeight.w800, color: isSelected ? AppColors.primary : AppColors.textPrimary)),
                const SizedBox(height: 6),
                if (dayAppts.isNotEmpty)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.2), borderRadius: BorderRadius.circular(10)),
                    child: Text('${dayAppts.length}', style: GoogleFonts.heebo(fontSize: 11, fontWeight: FontWeight.w700, color: AppColors.primary)),
                  ),
                if (holiday.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Tooltip(message: holiday.first.name, child: Text(holiday.first.name, style: GoogleFonts.heebo(fontSize: 9, fontWeight: FontWeight.w600, color: Colors.red), maxLines: 1, overflow: TextOverflow.ellipsis)),
                  ),
              ]),
            ),
          ),
        );
      }),
    );
  }

  // ── Monthly View ──

  Widget _buildMonthNav(AppointmentsState state, MedScribeThemeExtension ext) {
    final m = state.selectedMonth;
    final label = DateFormat('MMMM yyyy', context.locale.toString()).format(DateTime(m.year, m.month));
    final notifier = ref.read(appointmentsProvider.notifier);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: ext.cardDecoration,
      child: Row(children: [
        IconButton(icon: const Icon(Icons.chevron_right), onPressed: notifier.previousMonth, iconSize: 20, color: AppColors.textSecondary),
        const Spacer(),
        Text(label, style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const Spacer(),
        IconButton(icon: const Icon(Icons.chevron_left), onPressed: notifier.nextMonth, iconSize: 20, color: AppColors.textSecondary),
      ]),
    );
  }

  Widget _buildMonthGrid(AppointmentsState state, MedScribeThemeExtension ext) {
    final m = state.selectedMonth;
    final firstDay = DateTime(m.year, m.month, 1);
    final daysInMonth = DateTime(m.year, m.month + 1, 0).day;
    // Sunday = 0 offset for Israeli week (Sunday first)
    final firstWeekday = firstDay.weekday % 7; // Sunday=0, Mon=1...Sat=6
    final totalCells = ((firstWeekday + daysInMonth + 6) ~/ 7) * 7;

    return Column(children: [
      // Day headers
      Row(
        children: List.generate(7, (i) {
          final day = state.selectedMonth.add(Duration(days: i));
          return Expanded(
            child: Center(child: Text(DateFormat('E', context.locale.toString()).format(day).substring(0, 2), style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w700, color: AppColors.textMuted))),
          );
        }),
      ),
      const SizedBox(height: 8),
      // Grid
      ...List.generate(totalCells ~/ 7, (row) {
        return Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: Row(
            children: List.generate(7, (col) {
              final cellIndex = row * 7 + col;
              final dayNum = cellIndex - firstWeekday + 1;
              if (dayNum < 1 || dayNum > daysInMonth) {
                return Expanded(child: Container(height: 52, margin: const EdgeInsets.symmetric(horizontal: 2)));
              }
              final day = DateTime(m.year, m.month, dayNum);
              return Expanded(child: _buildMonthCell(day, state));
            }),
          ),
        );
      }),
    ]);
  }

  Widget _buildMonthCell(DateTime day, AppointmentsState state) {
    final isSelected = _sameDay(day, state.selectedDate);
    final isToday = _sameDay(day, DateTime.now());
    final dayAppts = state.appointments.where((a) => _sameDay(a.startTime, day)).toList();
    final holiday = state.holidays.where((h) => h.date == _fmt(day)).toList();

    return GestureDetector(
      onTap: () => ref.read(appointmentsProvider.notifier).selectDate(day),
      child: Container(
        height: 52,
        margin: const EdgeInsets.symmetric(horizontal: 2),
        decoration: BoxDecoration(
          color: isToday ? AppColors.primary.withValues(alpha: 0.2) : isSelected ? AppColors.primary.withValues(alpha: 0.08) : null,
          border: isSelected ? Border.all(color: AppColors.primary, width: 2) : Border.all(color: AppColors.cardBorder.withValues(alpha: 0.5)),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text('${day.day}', style: GoogleFonts.heebo(fontSize: 14, fontWeight: isToday ? FontWeight.w900 : FontWeight.w600, color: isToday ? AppColors.primary : AppColors.textPrimary)),
          Row(mainAxisAlignment: MainAxisAlignment.center, mainAxisSize: MainAxisSize.min, children: [
            if (dayAppts.isNotEmpty)
              Container(
                margin: const EdgeInsets.only(top: 2),
                padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                decoration: BoxDecoration(color: AppColors.primary.withValues(alpha: 0.25), borderRadius: BorderRadius.circular(6)),
                child: Text('${dayAppts.length}', style: GoogleFonts.heebo(fontSize: 9, fontWeight: FontWeight.w700, color: AppColors.primary)),
              ),
            if (holiday.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 2, right: 2),
                child: Tooltip(message: holiday.first.name, child: Container(width: 6, height: 6, decoration: const BoxDecoration(color: Colors.red, shape: BoxShape.circle))),
              ),
          ]),
        ]),
      ),
    );
  }

  // ── Day Detail (shared) ──

  Widget _buildDayDetail(AppointmentsState state, MedScribeThemeExtension ext) {
    final sel = state.selectedDate;
    final dayAppts = state.appointments.where((a) => _sameDay(a.startTime, sel)).toList()..sort((a, b) => a.startTime.compareTo(b.startTime));
    final holiday = state.holidays.where((h) => h.date == _fmt(sel)).toList();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: ext.cardDecoration,
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text(DateFormat('EEEE, d MMMM', context.locale.toString()).format(sel), style: GoogleFonts.heebo(fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
          if (holiday.isNotEmpty) ...[
            const SizedBox(width: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(color: Colors.red.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(8)),
              child: Text(holiday.first.name, style: GoogleFonts.heebo(fontSize: 12, fontWeight: FontWeight.w600, color: Colors.red)),
            ),
          ],
        ]),
        const SizedBox(height: 16),
        if (dayAppts.isEmpty)
          Expanded(child: Center(child: Text('appointments.no_appointments_today'.tr(), style: GoogleFonts.heebo(fontSize: 14, color: AppColors.textMuted))))
        else
          Expanded(
            child: ListView.separated(
              itemCount: dayAppts.length,
              separatorBuilder: (_, __) => Divider(color: AppColors.cardBorder, height: 1),
              itemBuilder: (context, i) => _buildAppointmentTile(dayAppts[i]),
            ),
          ),
      ]),
    );
  }

  Widget _buildAppointmentTile(AppointmentModel appt) {
    final time = '${appt.startTime.hour.toString().padLeft(2, '0')}:${appt.startTime.minute.toString().padLeft(2, '0')}';
    final statusColor = switch (appt.status) {
      'completed' => AppColors.success,
      'cancelled' => Colors.red,
      'no_show' => AppColors.warning,
      _ => AppColors.primary,
    };

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Row(children: [
        Container(width: 4, height: 40, decoration: BoxDecoration(color: statusColor, borderRadius: BorderRadius.circular(2))),
        const SizedBox(width: 12),
        Text(time, style: GoogleFonts.heebo(fontSize: 15, fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        const SizedBox(width: 16),
        Expanded(
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(appt.title, style: GoogleFonts.heebo(fontSize: 14, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
            if (appt.patientName != null)
              GestureDetector(
                onTap: appt.patientId != null ? () => context.push('/patients/${appt.patientId}') : null,
                child: Text(appt.patientName!, style: GoogleFonts.heebo(fontSize: 12, color: AppColors.primary, decoration: TextDecoration.underline)),
              ),
          ]),
        ),
        if (appt.syncedToGoogle)
          Padding(padding: const EdgeInsets.only(left: 8), child: Icon(Icons.event, size: 16, color: AppColors.textMuted)),
        IconButton(icon: Icon(Icons.edit_outlined, size: 18, color: AppColors.textMuted), onPressed: () => _showEditDialog(appt)),
        IconButton(icon: Icon(Icons.delete_outline, size: 18, color: Colors.red.withValues(alpha: 0.7)), onPressed: () => _confirmDelete(appt)),
      ]),
    );
  }

  // ── Dialogs ──

  void _showCreateDialog() {
    final titleCtrl = TextEditingController();
    final descCtrl = TextEditingController();
    final patientSearchCtrl = TextEditingController();
    DateTime selectedDate = ref.read(appointmentsProvider).selectedDate;
    TimeOfDay selectedTime = const TimeOfDay(hour: 9, minute: 0);
    int duration = 20;
    bool syncGoogle = true;
    String? selectedPatientId;
    String? selectedPatientName;
    List<Map<String, dynamic>> patientResults = [];
    Timer? searchDebounce;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(builder: (ctx, setDialogState) {
        return AlertDialog(
          backgroundColor: AppColors.card,
          title: Text('appointments.create_title'.tr(), style: GoogleFonts.heebo(fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
          content: SizedBox(
            width: 400,
            child: SingleChildScrollView(
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                // Patient search
                TextField(
                  controller: patientSearchCtrl,
                  readOnly: selectedPatientId != null,
                  style: GoogleFonts.heebo(color: AppColors.textPrimary, fontSize: 14),
                  decoration: InputDecoration(
                    labelText: 'appointments.patient_label'.tr(),
                    labelStyle: GoogleFonts.heebo(color: AppColors.textMuted),
                    hintText: 'appointments.patient_search_hint'.tr(),
                    hintStyle: GoogleFonts.heebo(color: AppColors.textMuted.withValues(alpha: 0.5), fontSize: 13),
                    prefixIcon: Icon(Icons.person_search_rounded, size: 18, color: AppColors.textMuted),
                    suffixIcon: selectedPatientId != null
                        ? IconButton(icon: Icon(Icons.close, size: 16, color: AppColors.textMuted), onPressed: () {
                            setDialogState(() { selectedPatientId = null; selectedPatientName = null; patientSearchCtrl.clear(); patientResults = []; });
                          })
                        : null,
                  ),
                  onChanged: (q) {
                    searchDebounce?.cancel();
                    if (q.trim().isEmpty) { setDialogState(() => patientResults = []); return; }
                    searchDebounce = Timer(const Duration(milliseconds: 300), () async {
                      try {
                        final res = await api.get('/patients/search', queryParameters: {'q': q.trim()});
                        if (ctx.mounted) setDialogState(() => patientResults = List<Map<String, dynamic>>.from(res.data));
                      } catch (_) {}
                    });
                  },
                ),
                if (selectedPatientId != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Row(children: [
                      Icon(Icons.check_circle_rounded, size: 14, color: AppColors.success),
                      const SizedBox(width: 4),
                      Text('appointments.selected_patient'.tr(namedArgs: {'name': selectedPatientName!}), style: GoogleFonts.heebo(fontSize: 12, color: AppColors.success, fontWeight: FontWeight.w500)),
                    ]),
                  ),
                if (patientResults.isNotEmpty && selectedPatientId == null)
                  Container(
                    margin: const EdgeInsets.only(top: 4),
                    constraints: const BoxConstraints(maxHeight: 150),
                    decoration: BoxDecoration(border: Border.all(color: AppColors.cardBorder), borderRadius: BorderRadius.circular(8)),
                    child: ListView.separated(
                      shrinkWrap: true, padding: EdgeInsets.zero,
                      itemCount: patientResults.length,
                      separatorBuilder: (_, __) => Divider(height: 1, color: AppColors.cardBorder),
                      itemBuilder: (_, i) {
                        final p = patientResults[i];
                        return ListTile(
                          dense: true,
                          title: Text(p['name'] ?? '', style: GoogleFonts.heebo(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
                          subtitle: p['phone'] != null ? Text(p['phone'], style: GoogleFonts.heebo(fontSize: 11, color: AppColors.textMuted)) : null,
                          onTap: () => setDialogState(() {
                            selectedPatientId = p['id'];
                            selectedPatientName = p['name'];
                            patientSearchCtrl.text = p['name'] ?? '';
                            patientResults = [];
                          }),
                        );
                      },
                    ),
                  ),
                const SizedBox(height: 12),
                TextField(controller: titleCtrl, decoration: InputDecoration(labelText: 'appointments.title_label'.tr(), labelStyle: GoogleFonts.heebo(color: AppColors.textMuted)), style: GoogleFonts.heebo(color: AppColors.textPrimary)),
                const SizedBox(height: 12),
                TextField(controller: descCtrl, decoration: InputDecoration(labelText: 'appointments.notes_label'.tr(), labelStyle: GoogleFonts.heebo(color: AppColors.textMuted)), style: GoogleFonts.heebo(color: AppColors.textPrimary), maxLines: 2),
                const SizedBox(height: 16),
                Row(children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () async {
                        final picked = await showDatePicker(context: ctx, initialDate: selectedDate, firstDate: DateTime.now().subtract(const Duration(days: 30)), lastDate: DateTime.now().add(const Duration(days: 365)));
                        if (picked != null) setDialogState(() => selectedDate = picked);
                      },
                      icon: const Icon(Icons.calendar_today, size: 16),
                      label: Text('${selectedDate.day}/${selectedDate.month}/${selectedDate.year}', style: GoogleFonts.heebo(fontSize: 13)),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () async {
                        final picked = await showTimePicker(context: ctx, initialTime: selectedTime);
                        if (picked != null) setDialogState(() => selectedTime = picked);
                      },
                      icon: const Icon(Icons.access_time, size: 16),
                      label: Text('${selectedTime.hour.toString().padLeft(2, '0')}:${selectedTime.minute.toString().padLeft(2, '0')}', style: GoogleFonts.heebo(fontSize: 13)),
                    ),
                  ),
                ]),
                const SizedBox(height: 12),
                DropdownButtonFormField<int>(
                  value: duration,
                  decoration: InputDecoration(labelText: 'appointments.duration_label'.tr(), labelStyle: GoogleFonts.heebo(color: AppColors.textMuted)),
                  dropdownColor: AppColors.card,
                  style: GoogleFonts.heebo(color: AppColors.textPrimary),
                  items: [10, 15, 20, 30, 45, 60].map((d) => DropdownMenuItem(value: d, child: Text('appointments.minutes_label'.tr(namedArgs: {'count': d.toString()})))).toList(),
                  onChanged: (v) => setDialogState(() => duration = v!),
                ),
                const SizedBox(height: 12),
                CheckboxListTile(
                  value: syncGoogle,
                  onChanged: (v) => setDialogState(() => syncGoogle = v!),
                  title: Text('appointments.sync_google'.tr(), style: GoogleFonts.heebo(fontSize: 13, color: AppColors.textSecondary)),
                  controlAffinity: ListTileControlAffinity.leading,
                  activeColor: AppColors.primary,
                  contentPadding: EdgeInsets.zero,
                ),
              ]),
            ),
          ),
          actions: [
            TextButton(onPressed: () { searchDebounce?.cancel(); Navigator.pop(ctx); }, child: Text('common.cancel'.tr(), style: GoogleFonts.heebo(color: AppColors.textMuted))),
            ElevatedButton(
              onPressed: () {
                if (titleCtrl.text.isEmpty) return;
                searchDebounce?.cancel();
                final startTime = DateTime(selectedDate.year, selectedDate.month, selectedDate.day, selectedTime.hour, selectedTime.minute);
                ref.read(appointmentsProvider.notifier).createAppointment(patientId: selectedPatientId, title: titleCtrl.text, description: descCtrl.text.isNotEmpty ? descCtrl.text : null, startTime: startTime, durationMinutes: duration, syncToGoogle: syncGoogle);
                Navigator.pop(ctx);
              },
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white),
              child: Text('appointments.create_button'.tr(), style: GoogleFonts.heebo(fontWeight: FontWeight.w600)),
            ),
          ],
        );
      }),
    );
  }

  void _showEditDialog(AppointmentModel appt) {
    final titleCtrl = TextEditingController(text: appt.title);
    final descCtrl = TextEditingController(text: appt.description ?? '');
    String status = appt.status;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(builder: (ctx, setDialogState) {
        return AlertDialog(
          backgroundColor: AppColors.card,
          title: Text('appointments.edit_title'.tr(), style: GoogleFonts.heebo(fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
          content: SizedBox(
            width: 400,
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              TextField(controller: titleCtrl, decoration: InputDecoration(labelText: 'appointments.title_label'.tr()), style: GoogleFonts.heebo(color: AppColors.textPrimary)),
              const SizedBox(height: 12),
              TextField(controller: descCtrl, decoration: InputDecoration(labelText: 'appointments.notes_label'.tr()), style: GoogleFonts.heebo(color: AppColors.textPrimary), maxLines: 2),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: status,
                decoration: InputDecoration(labelText: 'appointments.status_label'.tr()),
                dropdownColor: AppColors.card,
                style: GoogleFonts.heebo(color: AppColors.textPrimary),
                items: [
                  DropdownMenuItem(value: 'scheduled', child: Text('status.scheduled'.tr())),
                  DropdownMenuItem(value: 'completed', child: Text('status.completed'.tr())),
                  DropdownMenuItem(value: 'cancelled', child: Text('status.cancelled'.tr())),
                  DropdownMenuItem(value: 'no_show', child: Text('status.no_show'.tr())),
                ],
                onChanged: (v) => setDialogState(() => status = v!),
              ),
            ]),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: Text('common.cancel'.tr(), style: GoogleFonts.heebo(color: AppColors.textMuted))),
            ElevatedButton(
              onPressed: () {
                ref.read(appointmentsProvider.notifier).updateAppointment(appt.id, {'title': titleCtrl.text, 'description': descCtrl.text, 'status': status});
                Navigator.pop(ctx);
              },
              style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white),
              child: Text('common.save'.tr(), style: GoogleFonts.heebo(fontWeight: FontWeight.w600)),
            ),
          ],
        );
      }),
    );
  }

  void _confirmDelete(AppointmentModel appt) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.card,
        title: Text('appointments.delete_title'.tr(), style: GoogleFonts.heebo(fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        content: Text('appointments.delete_confirm'.tr(namedArgs: {'title': appt.title}), style: GoogleFonts.heebo(color: AppColors.textSecondary)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text('common.cancel'.tr(), style: GoogleFonts.heebo(color: AppColors.textMuted))),
          ElevatedButton(
            onPressed: () { ref.read(appointmentsProvider.notifier).deleteAppointment(appt.id); Navigator.pop(ctx); },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
            child: Text('common.delete'.tr(), style: GoogleFonts.heebo(fontWeight: FontWeight.w600)),
          ),
        ],
      ),
    );
  }

  Future<void> _connectCalendar() async {
    final url = await ref.read(appointmentsProvider.notifier).getCalendarAuthUrl();
    if (url != null && mounted) {
      final uri = Uri.parse(url);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('common.cannot_open_link'.tr()), backgroundColor: Colors.red));
        }
      }
    }
  }

  bool _sameDay(DateTime a, DateTime b) => a.year == b.year && a.month == b.month && a.day == b.day;
  String _fmt(DateTime d) => '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
}
