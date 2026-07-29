import 'package:eva_icons_flutter/eva_icons_flutter.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('icons retain their font metadata and code points', () {
    expect(
      EvaIcons.activity,
      const IconData(
        0xea01,
        fontFamily: 'EvaIcons',
        fontPackage: 'eva_icons_flutter',
      ),
    );
    expect(EvaIcons.wifi.codePoint, 0xebea);
    expect(EvaIcons.wifi.fontFamily, 'EvaIcons');
    expect(EvaIcons.wifi.fontPackage, 'eva_icons_flutter');
  });
}
