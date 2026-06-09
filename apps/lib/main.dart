import 'package:flutter/material.dart';
import 'features/matches/match_checkout_screen.dart';

void main() {
  runApp(const TicketMafiaApp());
}

class TicketMafiaApp extends StatelessWidget {
  const TicketMafiaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(home: MatchCheckoutScreen());
  }
}
