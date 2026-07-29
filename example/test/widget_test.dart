import 'package:eva_icons_demo/main.dart';
import 'package:eva_icons_flutter/eva_icons_flutter.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('renders the Eva Icons demo', (tester) async {
    await tester.pumpWidget(MyApp());

    expect(find.text('Eva Icon Demo'), findsOneWidget);
    expect(find.byIcon(EvaIcons.heart), findsOneWidget);
    expect(find.byIcon(EvaIcons.emailOutline), findsOneWidget);
  });
}
