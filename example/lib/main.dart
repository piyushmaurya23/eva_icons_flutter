import 'package:flutter/material.dart';
import 'package:eva_icons_flutter/eva_icons_flutter.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Eva Icons Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(icon: Icon(EvaIcons.menu), onPressed: () {}),
        title: Text('Eva Icon Demo'),
        actions: <Widget>[
          IconButton(icon: Icon(EvaIcons.moreVertical), onPressed: () {})
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Row(
              children: <Widget>[
                Icon(EvaIcons.arrowBack),
                SizedBox(width: 10.0),
                Text('Arrow Back Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.heart),
                SizedBox(width: 10.0),
                Text('Heart Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.twitter),
                SizedBox(width: 10.0),
                Text('Twitter Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.arrowCircleRight),
                SizedBox(width: 10.0),
                Text('Arrow Circle Right Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.home),
                SizedBox(width: 10.0),
                Text('Home Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.cloudUpload),
                SizedBox(width: 10.0),
                Text('Cloud Upload Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.codeDownload),
                SizedBox(width: 10.0),
                Text('Code Download Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.doneAllOutline),
                SizedBox(width: 10.0),
                Text('Done All Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.emailOutline),
                SizedBox(width: 10.0),
                Text('Email Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.swapOutline),
                SizedBox(width: 10.0),
                Text('Swap Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.radioOutline),
                SizedBox(width: 10.0),
                Text('Radio Icon')
              ],
            ),
            Row(
              children: <Widget>[
                Icon(EvaIcons.options2Outline),
                SizedBox(width: 10.0),
                Text('Options Icon')
              ],
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        child: Icon(EvaIcons.plus),
      ),
    );
  }
}
