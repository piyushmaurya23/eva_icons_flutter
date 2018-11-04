library eva_icons_flutter;

import 'package:flutter/widgets.dart';

class EvaIconData extends IconData {
  const EvaIconData(int codePoint)
      : super(
    codePoint,
    fontFamily: 'EvaIcons',
    fontPackage: 'eva_icons_flutter',
  );
}