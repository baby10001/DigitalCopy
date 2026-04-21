import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'screens/welcome_screen.dart';
import 'screens/dashboard_screen.dart';

import 'package:flutter_dotenv/flutter_dotenv.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  try {
    await dotenv.load(fileName: ".env");
  } catch (e) {
    debugPrint("Dotenv failed to load. Are you missing the .env file?");
  }
  
  try {
    if (kIsWeb) {
      // Use the provided web configuration
      await Firebase.initializeApp(
        options: const FirebaseOptions(
          apiKey: "yourrrrrrrr-keyyyyy",
          authDomain: "digitalcopy-9f237.firebaseapp.com",
          projectId: "digitalcopy-9f237",
          storageBucket: "digitalcopy-9f237.firebasestorage.app",
          messagingSenderId: "458069497914",
          appId: "1:458069497914:web:2d66cf7ecb0986846afd03",
          measurementId: "G-4X3LLG0K72",
        ),
      );
    } else {
      // For other platforms, rely on native config files 
      // (google-services.json / GoogleService-Info.plist)
      await Firebase.initializeApp();
    }
  } catch (e) {
    debugPrint("Firebase initialization failed: $e");
  }

  runApp(const DigitalCopyApp());
}

class DigitalCopyApp extends StatelessWidget {
  const DigitalCopyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Digital Copy',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        colorScheme: const ColorScheme.dark(
          primary: Colors.tealAccent,
          secondary: Colors.teal,
          surface: Color(0xFF1E1E1E),
        ),
        scaffoldBackgroundColor: const Color(0xFF121212),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF121212),
          elevation: 0,
        ),
        cardTheme: CardThemeData(
          color: const Color(0xFF1E1E1E),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        ),
      ),
      home: const AuthWrapper(),
    );
  }
}

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    // If Firebase isn't properly initialized yet, this stream won't work in a real app
    // However, it will at least show the WelcomeScreen gracefully if FirebaseAuth fails.
    try {
      return StreamBuilder<User?>(
        stream: FirebaseAuth.instance.authStateChanges(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(
              body: Center(child: CircularProgressIndicator()),
            );
          }
          if (snapshot.hasData) {
            return const DashboardScreen();
          }
          return const WelcomeScreen();
        },
      );
    } catch (e) {
      // Fallback for UI-only testing before Firebase setup
      return const WelcomeScreen();
    }
  }
}
