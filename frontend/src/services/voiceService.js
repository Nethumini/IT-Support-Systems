/**
 * Voice Input Service using Web Speech API
 * Provides speech-to-text functionality for the chat interface
 */

class VoiceService {
  constructor() {
    this.recognition = null
    this.isSupported = false
    this.isListening = false
    this.onResultCallback = null
    this.onErrorCallback = null
    this.onStartCallback = null
    this.onEndCallback = null
    
    this.init()
  }

  init() {
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported in this browser')
      this.isSupported = false
      return
    }

    this.isSupported = true
    this.recognition = new SpeechRecognition()
    
    // Configure recognition settings
    this.recognition.continuous = false  // Stop after user stops speaking
    this.recognition.interimResults = true  // Show interim results while speaking
    this.recognition.lang = 'en-US'  // Set language
    
    // Set up event handlers
    this.recognition.onstart = () => {
      this.isListening = true
      if (this.onStartCallback) {
        this.onStartCallback()
      }
    }

    this.recognition.onresult = (event) => {
      let interimTranscript = ''
      let finalTranscript = ''

      // Process all results
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' '
        } else {
          interimTranscript += transcript
        }
      }

      // Call callback with results
      if (this.onResultCallback) {
        this.onResultCallback({
          interim: interimTranscript,
          final: finalTranscript.trim()
        })
      }
    }

    this.recognition.onerror = (event) => {
      this.isListening = false
      
      let errorMessage = 'Speech recognition error occurred'
      
      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.'
          break
        case 'audio-capture':
          errorMessage = 'No microphone found. Please check your microphone settings.'
          break
        case 'not-allowed':
          errorMessage = 'Microphone permission denied. Please allow microphone access.'
          break
        case 'network':
          errorMessage = 'Network error. Please check your connection.'
          break
        case 'aborted':
          // User stopped manually, not an error
          return
        default:
          errorMessage = `Speech recognition error: ${event.error}`
      }

      if (this.onErrorCallback) {
        this.onErrorCallback(errorMessage)
      }
    }

    this.recognition.onend = () => {
      this.isListening = false
      if (this.onEndCallback) {
        this.onEndCallback()
      }
    }
  }

  /**
   * Start listening for voice input
   */
  startListening() {
    if (!this.isSupported) {
      throw new Error('Speech recognition is not supported in this browser')
    }

    if (this.isListening) {
      console.warn('Already listening')
      return
    }

    try {
      this.recognition.start()
    } catch (error) {
      // Recognition might already be starting
      if (error.name !== 'InvalidStateError') {
        console.error('Error starting speech recognition:', error)
        if (this.onErrorCallback) {
          this.onErrorCallback('Failed to start voice input. Please try again.')
        }
      }
    }
  }

  /**
   * Stop listening for voice input
   */
  stopListening() {
    if (!this.isSupported || !this.isListening) {
      return
    }

    try {
      this.recognition.stop()
    } catch (error) {
      console.error('Error stopping speech recognition:', error)
    }
  }

  /**
   * Abort current recognition
   */
  abort() {
    if (!this.isSupported) {
      return
    }

    try {
      this.recognition.abort()
      this.isListening = false
    } catch (error) {
      console.error('Error aborting speech recognition:', error)
    }
  }

  /**
   * Set callback for recognition results
   */
  onResult(callback) {
    this.onResultCallback = callback
  }

  /**
   * Set callback for errors
   */
  onError(callback) {
    this.onErrorCallback = callback
  }

  /**
   * Set callback for when recognition starts
   */
  onStart(callback) {
    this.onStartCallback = callback
  }

  /**
   * Set callback for when recognition ends
   */
  onEnd(callback) {
    this.onEndCallback = callback
  }

  /**
   * Check if speech recognition is supported
   */
  checkSupport() {
    return this.isSupported
  }

  /**
   * Get current listening state
   */
  getListeningState() {
    return this.isListening
  }

  /**
   * Set language for recognition
   */
  setLanguage(lang) {
    if (this.recognition) {
      this.recognition.lang = lang
    }
  }
}

// Export singleton instance
export const voiceService = new VoiceService()

// Export class for testing
export default VoiceService

