import 'package:flutter/material.dart';

// Sprint: v1 | Feature: FR-011,FR-012,BR-007 | US: US-012 | Task Group: TG 1.6 Seat Exchange and Local Demo Runtime
// Contract: design-system-v1.md SCREEN-012 mobile shell; api-specs-v1.md API-014 future service integration
class SeatExchangeScreen extends StatefulWidget {
  const SeatExchangeScreen({super.key});

  @override
  State<SeatExchangeScreen> createState() => _SeatExchangeScreenState();
}

class _SeatExchangeScreenState extends State<SeatExchangeScreen> {
  final int currentPriceVnd = 100000;
  final List<_ExchangeSeat> seats = const [
    _ExchangeSeat('seat-higher', 'B-T1-001', 150000, 'AVAILABLE'),
    _ExchangeSeat('seat-equal', 'A-T1-002', 100000, 'AVAILABLE'),
    _ExchangeSeat('seat-cheaper', 'C-T1-001', 80000, 'AVAILABLE'),
    _ExchangeSeat('seat-held', 'D-T1-001', 160000, 'HELD'),
  ];
  _ExchangeSeat? selectedSeat;
  String state = 'populated';

  @override
  Widget build(BuildContext context) {
    if (state == 'empty') {
      return const Scaffold(body: Center(child: Text('Không có ghế phù hợp để đổi.')));
    }
    if (state == 'error') {
      return const Scaffold(body: Center(child: Text('Chỉ được đổi sang ghế có giá bằng hoặc cao hơn.')));
    }
    if (state == 'confirmed') {
      return const Scaffold(body: Center(child: Text('Đơn đổi ghế đã được tạo.')));
    }
    return Scaffold(
      appBar: AppBar(title: const Text('Đổi ghế')),
      body: Semantics(
        identifier: 'exchange-seat-grid',
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text('Ghế hiện tại: A-T1-001'),
            for (final seat in seats)
              OutlinedButton(
                key: Key('exchange-seat-${seat.id}'),
                onPressed: _eligible(seat) ? () => setState(() => selectedSeat = seat) : null,
                child: Text('${seat.seatCode} · ${seat.priceVnd} VND'),
              ),
            FilledButton(
              onPressed: selectedSeat == null ? null : _continueExchange,
              child: const Text('Tiếp tục đổi ghế'),
            ),
          ],
        ),
      ),
    );
  }

  bool _eligible(_ExchangeSeat seat) {
    return seat.status == 'AVAILABLE' && seat.priceVnd >= currentPriceVnd;
  }

  void _continueExchange() {
    if (selectedSeat == null || !_eligible(selectedSeat!)) {
      setState(() => state = 'error');
      return;
    }
    setState(() => state = 'confirmed');
  }
}

class _ExchangeSeat {
  const _ExchangeSeat(this.id, this.seatCode, this.priceVnd, this.status);

  final String id;
  final String seatCode;
  final int priceVnd;
  final String status;
}
