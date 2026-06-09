import 'package:flutter/material.dart';

// Sprint: v1 | Feature: FR-009,FR-010,NFR-003 | US: US-009,US-010,US-011 | Task Group: TG 1.5 Purchase History, Ticket Detail, and One-Time Scan
// Contract: design-system-v1.md SCREEN-009/SCREEN-010/SCREEN-011 mobile shell; api-specs-v1.md API-008/API-009 future service integration
class TicketHistoryScreen extends StatefulWidget {
  const TicketHistoryScreen({super.key});

  @override
  State<TicketHistoryScreen> createState() => _TicketHistoryScreenState();
}

class _TicketHistoryScreenState extends State<TicketHistoryScreen> {
  final List<_TicketOrder> orders = const [
    _TicketOrder('order-1', 'Hanoi FC vs Saigon FC', 'ISSUED', 120000, [
      _Ticket('ticket-1', 'A-T1-001', 'ISSUED', 'tk_v1_signedopaque'),
      _Ticket('ticket-2', 'A-T1-002', 'CANCELLED', null),
    ]),
  ];
  _Ticket? selectedTicket;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Lịch sử mua vé')),
      body: Semantics(
        identifier: selectedTicket == null ? 'ticket-history-list' : 'ticket-detail',
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: selectedTicket == null ? _historyList() : _ticketDetail(selectedTicket!),
        ),
      ),
    );
  }

  Widget _historyList() {
    if (orders.isEmpty) {
      return const Text('Bạn chưa có đơn mua vé nào.');
    }
    return ListView(
      children: [
        for (final order in orders)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(order.matchName, style: Theme.of(context).textTheme.titleMedium),
                  Text('${order.status} · ${order.totalAmountVnd} VND'),
                  for (final ticket in order.tickets)
                    TextButton(
                      onPressed: () => setState(() => selectedTicket = ticket),
                      child: Text('${ticket.seatCode} · ${ticket.status}'),
                    ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _ticketDetail(_Ticket ticket) {
    final entryValid = ticket.status == 'ISSUED' && ticket.qrToken != null;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        TextButton(
          onPressed: () => setState(() => selectedTicket = null),
          child: const Text('Lịch sử mua vé'),
        ),
        Text(ticket.seatCode, style: Theme.of(context).textTheme.headlineSmall),
        Text(ticket.status, key: const Key('ticket-status')),
        if (entryValid)
          Container(
            key: const Key('ticket-qr-card'),
            margin: const EdgeInsets.only(top: 12),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(border: Border.all(color: Colors.black87)),
            child: Text(ticket.qrToken!),
          )
        else
          const Padding(
            padding: EdgeInsets.only(top: 12),
            child: Text('Vé này không còn hợp lệ để vào sân.'),
          ),
      ],
    );
  }
}

class _TicketOrder {
  const _TicketOrder(this.id, this.matchName, this.status, this.totalAmountVnd, this.tickets);

  final String id;
  final String matchName;
  final String status;
  final int totalAmountVnd;
  final List<_Ticket> tickets;
}

class _Ticket {
  const _Ticket(this.id, this.seatCode, this.status, this.qrToken);

  final String id;
  final String seatCode;
  final String status;
  final String? qrToken;
}
