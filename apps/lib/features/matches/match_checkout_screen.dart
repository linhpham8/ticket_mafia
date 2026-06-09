import 'package:flutter/material.dart';

// Sprint: v1 | Feature: FR-002,FR-003,FR-004,FR-005 | US: US-002..US-005 | Task Group: TG 1.3 User Browse, Seat Selection, Checkout Hold, and Payment Completion
// Contract: design-system-v1.md SCREEN-002..SCREEN-005 mobile shell; api-specs-v1.md API-003..API-006 future service integration
class MatchCheckoutScreen extends StatefulWidget {
  const MatchCheckoutScreen({super.key});

  @override
  State<MatchCheckoutScreen> createState() => _MatchCheckoutScreenState();
}

class _MatchCheckoutScreenState extends State<MatchCheckoutScreen> {
  final List<_Seat> seats = List.generate(
    6,
    (index) => _Seat('seat-${index + 1}', 'A-T1-00${index + 1}', 120000),
  );
  final Set<String> selectedSeatIds = {};
  String stateId = 'matches-list';
  String message = '';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Vé bóng đá')),
      body: Semantics(
        identifier: stateId,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: _body(),
        ),
      ),
    );
  }

  Widget _body() {
    if (stateId == 'matches-list') {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('Hanoi FC vs Saigon FC'),
          const Text('OPEN_FOR_SALE'),
          ElevatedButton(
            onPressed: () => setState(() => stateId = 'seat-map-grid'),
            child: const Text('Chọn ghế'),
          ),
        ],
      );
    }
    if (stateId == 'checkout-qr') {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text('Còn 10:00 để giữ ghế'),
          Text('Tổng tiền: ${selectedSeatIds.length * 120000} VND'),
          const Text('asset://payment/default'),
          ElevatedButton(
            onPressed: () => setState(() => stateId = 'pending-confirmation'),
            child: const Text('Tôi đã chuyển khoản'),
          ),
        ],
      );
    }
    if (stateId == 'pending-confirmation') {
      return const Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Đang chờ admin xác nhận'),
          Text('Admin sẽ kiểm tra trong 10 phút'),
        ],
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: seats.map((seat) {
            final selected = selectedSeatIds.contains(seat.id);
            return ChoiceChip(
              label: Text('${seat.code}\n${seat.priceVnd} VND'),
              selected: selected,
              onSelected: (_) => _toggleSeat(seat),
            );
          }).toList(),
        ),
        if (message.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Text(message, key: const Key('seat-limit-message')),
          ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Text('${selectedSeatIds.length}/5 ghế đã chọn'),
        ),
        ElevatedButton(
          onPressed: selectedSeatIds.isEmpty ? null : () => setState(() => stateId = 'checkout-qr'),
          child: const Text('Thanh toán'),
        ),
      ],
    );
  }

  void _toggleSeat(_Seat seat) {
    setState(() {
      if (selectedSeatIds.contains(seat.id)) {
        selectedSeatIds.remove(seat.id);
        return;
      }
      if (selectedSeatIds.length >= 5) {
        message = 'Bạn chỉ có thể chọn tối đa 5 ghế cho mỗi lần mua.';
        return;
      }
      selectedSeatIds.add(seat.id);
      message = '';
    });
  }
}

class _Seat {
  const _Seat(this.id, this.code, this.priceVnd);

  final String id;
  final String code;
  final int priceVnd;
}
