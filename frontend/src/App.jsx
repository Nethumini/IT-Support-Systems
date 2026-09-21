import { useState, useEffect, useRef } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom'
import { fetchBackendStatus, sendChatMessage, resetChatConversation, sendChatMessageWithImage } from './api'
import { Bot, User, Send, FileText, AlertCircle, Zap, Wrench, HelpCircle, Mic, MicOff, Image, X, CheckCircle, XCircle } from 'lucide-react'
import { STORAGE_KEYS } from './config/constants'
import { voiceService } from './services/voiceService'
import actionService from './services/actionService'
import { remediationService } from './services/remediationService'
import ActionModal, { ActionSuggestions } from './components/ActionModal'
import RiskCard, { verificationText } from './components/RiskCard'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import TicketList from './components/TicketList'
import SystemMonitoring from './components/SystemMonitoring'
import Reports from './components/Reports'
import Settings from './components/Settings'
import AutomationPage from './components/AutomationPage'
import ErrorCodesPage from './components/ErrorCodesPage'
import QuickActionsPage from './components/QuickActionsPage'
import KnowledgeBasePage from './components/KnowledgeBasePage'
import UserManagement from './components/UserManagement'
import AuditLogs from './components/AuditLogs'
import Login from './components/Login'
import Register from './components/Register'
import './styles/App.css'
import './styles/agent-mode.css'
import './styles/components/PermissionComponents.css'

function ChatPage({ user }) {
  const location = useLocation()  // Track navigation to detect when coming from tickets
  const [backendStatus, setBackendStatus] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [currentTicket, setCurrentTicket] = useState(null)
  const [currentSessionId, setCurrentSessionId] = useState(null)  // Track session ID
  const [isListening, setIsListening] = useState(false)
  const [voiceSupported, setVoiceSupported] = useState(false)
  const [interimTranscript, setInterimTranscript] = useState('')
  
  // Action execution state
  const [showActionModal, setShowActionModal] = useState(false)
  const [selectedAction, setSelectedAction] = useState(null)
  const [actionExecuting, setActionExecuting] = useState(false)
  const [actionResult, setActionResult] = useState(null)
  const [pendingActionRequest, setPendingActionRequest] = useState(null)
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [initKey, setInitKey] = useState(0)  // Force re-initialization
  
  // Step-by-step troubleshooting state
  const [remainingActions, setRemainingActions] = useState([])
  const [troubleshootingStep, setTroubleshootingStep] = useState(0)
  const [awaitingFeedback, setAwaitingFeedback] = useState(false)
  const [executedActionIds, setExecutedActionIds] = useState(new Set())  // Track executed actions
  
  // Agent Mode state
  const [agentMode, setAgentMode] = useState(false)
  const [agentModeTipShown, setAgentModeTipShown] = useState(false)  // Track if tip was shown
  
  const messagesEndRef = useRef(null)
  const interimTranscriptRef = useRef('')
  const fileInputRef = useRef(null)

  // Storage keys for chat persistence
  const CHAT_STORAGE_KEY = `it_support_systems_chat_${user?.email || 'guest'}`
  const SESSION_STORAGE_KEY = `it_support_systems_session_${user?.email || 'guest'}`
  const TICKET_STORAGE_KEY = `it_support_systems_ticket_${user?.email || 'guest'}`
  const RESUME_TICKET_KEY = `it_support_systems_resume_ticket_${user?.email || 'guest'}`

  // Initialize messages from localStorage (resume context is handled in separate useEffect)
  useEffect(() => {
    // Skip if we have a resume context - let the other useEffect handle it
    const resumeContext = localStorage.getItem(RESUME_TICKET_KEY)
    if (resumeContext) {
      return  // Will be handled by the navigation useEffect
    }

    // Normal initialization - check for saved messages
    const savedMessages = localStorage.getItem(CHAT_STORAGE_KEY)
    const savedSession = localStorage.getItem(SESSION_STORAGE_KEY)
    const savedTicket = localStorage.getItem(TICKET_STORAGE_KEY)

    if (savedMessages) {
      try {
        const parsed = JSON.parse(savedMessages)
        if (parsed && parsed.length > 0) {
          setMessages(parsed)
          if (savedSession) setCurrentSessionId(savedSession)
          if (savedTicket) setCurrentTicket(parseInt(savedTicket))
          return
        }
      } catch (e) {
        console.warn('Failed to parse saved messages:', e)
      }
    }

    // Default welcome message if no saved messages
    setMessages([
      { 
        role: 'assistant', 
        content: `Hi ${user?.name || 'there'}! I'm your AI IT Support Assistant. How can I help you today?`,
        timestamp: new Date().toISOString()
      }
    ])
  }, [user?.email, location.key])  // Re-run when navigating to chat page

  // Check for resume context on every render (in case navigation doesn't trigger useEffect)
  useEffect(() => {
    const resumeContext = localStorage.getItem(RESUME_TICKET_KEY)
    if (resumeContext) {
      // We have a resume context - process it immediately
      try {
        const context = JSON.parse(resumeContext)
        // Clear the resume context immediately
        localStorage.removeItem(RESUME_TICKET_KEY)
        
        // Clear old saved chat
        localStorage.removeItem(CHAT_STORAGE_KEY)
        localStorage.removeItem(SESSION_STORAGE_KEY)
        localStorage.removeItem(TICKET_STORAGE_KEY)
        
        // Reset backend conversation to prevent cross-ticket contamination
        if (user?.email) {
          resetChatConversation(user.email).catch(err => {
            console.warn('Failed to reset backend conversation:', err)
          })
        }
        
        // Set ticket context
        setCurrentTicket(context.ticketId)
        setCurrentSessionId(null)
        
        if (context.resumeChat && context.existingMessages?.length > 0) {
          // Resume existing chat - load the previous messages
          const formattedMessages = context.existingMessages.map(msg => ({
            role: msg.role,
            content: msg.content,
            timestamp: msg.created_at || new Date().toISOString(),
            ticketId: context.ticketId
          }))
          
          // Add continuation message
          formattedMessages.push({
            role: 'assistant',
            content: `Continuing conversation for Ticket #${context.ticketId}: "${context.ticketTitle}"\n\nHow can I help you further with this issue?`,
            timestamp: new Date().toISOString(),
            ticketId: context.ticketId
          })
          
          setMessages(formattedMessages)
          localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(formattedMessages))
          localStorage.setItem(TICKET_STORAGE_KEY, context.ticketId.toString())
        } else if (context.isManualTicket) {
          // Manual ticket - start fresh
          const welcomeMessage = {
            role: 'assistant',
            content: `Hi! I'm here to help with Ticket #${context.ticketId}: "${context.ticketTitle}"\n\n**Issue Description:**\n${context.ticketDescription}\n\n**Priority:** ${context.ticketPriority}\n\nLet me help you troubleshoot this issue. Could you provide more details about when this problem started or any error messages you've seen?`,
            timestamp: new Date().toISOString(),
            ticketId: context.ticketId
          }
          setMessages([welcomeMessage])
          localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify([welcomeMessage]))
          localStorage.setItem(TICKET_STORAGE_KEY, context.ticketId.toString())
        }
      } catch (e) {
        console.warn('Failed to parse resume context:', e)
        localStorage.removeItem(RESUME_TICKET_KEY)
      }
    }
  }, [location])  // Run on every navigation

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      // Don't save image previews to avoid localStorage quota issues
      const messagesToSave = messages.map(msg => ({
        ...msg,
        imagePreview: msg.imagePreview ? '[image attached]' : undefined
      }))
      localStorage.setItem(CHAT_STORAGE_KEY, JSON.stringify(messagesToSave))
    }
  }, [messages])

  // Save session and ticket to localStorage
  useEffect(() => {
    if (currentSessionId) {
      localStorage.setItem(SESSION_STORAGE_KEY, currentSessionId)
    }
  }, [currentSessionId])

  useEffect(() => {
    if (currentTicket) {
      localStorage.setItem(TICKET_STORAGE_KEY, currentTicket.toString())
    }
  }, [currentTicket])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    fetchBackendStatus()
      .then(data => setBackendStatus(data))
      .catch(err => console.error('Backend status check failed:', err))
    
    // Don't auto-reset conversation - allow continuing previous chats
    // User can start new chat via "New Chat" button if needed

    // Initialize voice service
    setVoiceSupported(voiceService.checkSupport())
    
    // Set up voice recognition callbacks
    voiceService.onResult((result) => {
      if (result.final) {
        // Final transcript - set it in input field
        setInput(result.final)
        setInterimTranscript('')
        interimTranscriptRef.current = ''
        setIsListening(false)
      } else {
        // Interim transcript - show it temporarily
        setInterimTranscript(result.interim)
        interimTranscriptRef.current = result.interim
      }
    })

    voiceService.onError((error) => {
      setIsListening(false)
      setInterimTranscript('')
      interimTranscriptRef.current = ''
      // Show error message to user
      const errorMessage = {
        role: 'assistant',
        content: `Voice input error: ${error}`,
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    })

    voiceService.onStart(() => {
      setIsListening(true)
      setInterimTranscript('Listening...')
      interimTranscriptRef.current = 'Listening...'
    })

    voiceService.onEnd(() => {
      setIsListening(false)
      const currentInterim = interimTranscriptRef.current
      if (currentInterim && !currentInterim.includes('Listening')) {
        // Keep the interim transcript if it's actual speech
        setInput(prev => prev + (prev ? ' ' : '') + currentInterim)
      }
      setInterimTranscript('')
      interimTranscriptRef.current = ''
    })

    // Cleanup on unmount
    return () => {
      if (voiceService.getListeningState()) {
        voiceService.stopListening()
      }
    }
  }, [user?.email])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await sendChatMessage(messages.concat(userMessage), user.email, currentTicket, currentSessionId, agentMode)
      
      const assistantMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
        ticketId: response.ticket_id,
        action: response.action,
        priorityInfo: response.priority_info,
        needsClarification: response.needs_clarification,
        suggestedActions: response.suggested_actions,  // First action only (step-by-step)
        citations: response.citations,  // Approved KB articles this answer is grounded in
        troubleshootingStep: response.metadata?.troubleshooting_step,
        totalSteps: response.metadata?.total_steps,
        // Only show agent mode tip if not shown before and not in agent mode
        agentModeSuggestion: (response.agent_mode_suggestion && !agentMode && !agentModeTipShown) 
          ? response.agent_mode_suggestion 
          : null
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Mark tip as shown if backend suggests it (only once per session)
      if (response.agent_mode_suggestion && !agentMode && !agentModeTipShown) {
        setAgentModeTipShown(true)
      }
      
      // Track remaining actions for step-by-step troubleshooting
      if (response.metadata?.remaining_actions && response.metadata.remaining_actions.length > 0) {
        setRemainingActions(response.metadata.remaining_actions)
        setTroubleshootingStep(response.metadata.troubleshooting_step || 1)
      } else {
        setRemainingActions([])
        setTroubleshootingStep(0)
      }
      
      // Track session and ticket from response
      if (response.session_id && !currentSessionId) {
        setCurrentSessionId(response.session_id)
      }
      if (response.ticket_id && !currentTicket) {
        setCurrentTicket(response.ticket_id)
      }

    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.message}. Please check if the backend is running.`,
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  // Helper function to get LLM interpretation of action results
  /**
   * What a verified action found, put back into the conversation.
   *
   * Without this the result stops inside the risk card: the assistant then
   * asks the user to check by hand what it has already checked, because its
   * own reading was never part of the history it reasons over. Appending it as
   * an assistant message puts the observed state where the next turn can use
   * it, and costs no extra model call.
   */
  const handleActionOutcome = (action, outcome) => {
    const parts = [`**${action.name}** — ${verificationText(outcome)}`]

    if (outcome?.post_check?.reason) parts.push(outcome.post_check.reason)

    const output = outcome?.execution_result?.output
    if (output !== null && output !== undefined && output !== '') {
      const text = typeof output === 'string' ? output.trim() : JSON.stringify(output, null, 2)
      if (text) parts.push('```\n' + text + '\n```')
    }

    // An escalation says why nobody may proceed; that belongs in the thread too.
    if (outcome?.status === 'escalated' && outcome.escalation_reason) {
      parts.push(outcome.escalation_reason)
    }

    setMessages(prev => [...prev, {
      role: 'assistant',
      content: parts.join('\n\n'),
      timestamp: new Date().toISOString(),
      isActionResult: true
    }])
  }

  const getActionResultInterpretation = async (actionName, output, isSuccess) => {
    try {
      // Send the action result to chat for LLM interpretation
      const interpretationPrompt = `[SYSTEM: The user ran "${actionName}" and got this result. Your job is to:
1. Explain what this means in simple, friendly language (no technical jargon)
2. Tell them if this is good news or if action is needed
3. If there's a problem (like high memory 92%), suggest the NEXT specific step to take
4. Keep it conversational and empathetic - avoid robotic responses
5. Keep response concise (2-3 sentences max)

Example good response: "Your memory is at 92% which is quite high! This is likely why things feel slow. Let's free up some space by optimizing memory - I'll suggest that next."

Result:
${typeof output === 'string' ? output : JSON.stringify(output, null, 2)}`
      
      const response = await sendChatMessage(
        [...messages, { role: 'user', content: interpretationPrompt }],
        user.email,
        currentTicket,
        currentSessionId
      )
      return response.message
    } catch (e) {
      console.warn('Failed to get LLM interpretation:', e)
      return null
    }
  }

  // Handle action selection from suggestions
  const handleSelectAction = async (action) => {
    // Get parameters - suggested_params are actual values, parameters is the schema
    const params = action.suggested_params || {}
    
    // Track this action as executed
    setExecutedActionIds(prev => new Set([...prev, action.id]))
    
    // AGENT MODE: Always show permission modal for transparency and user control
    // Even low-risk actions should be confirmed when in Agent Mode
    if (false) {  // Disabled auto-execution - always show modal in Agent Mode
      try {
        setActionExecuting(true)
        setLoading(true)  // Show typing indicator
        
        const result = await actionService.executeActionDirectly(action.id, params, user.email)
        
        // Get raw output
        const rawOutput = result.result?.output || ''
        const outputStr = typeof rawOutput === 'string' ? rawOutput : JSON.stringify(rawOutput, null, 2)
        
        // Get follow-up actions from the result (Phase 1: Result-based suggestions)
        const followupActions = result.result?.followup_actions || []
        
        // Get LLM interpretation of the result for better UX
        let interpretation = null
        if (result.success && outputStr) {
          interpretation = await getActionResultInterpretation(action.name, outputStr, result.success)
        }
        
        // Determine next steps: Use followup_actions if available, otherwise use remainingActions
        let nextActions = []
        if (followupActions.length > 0) {
          // Filter out already executed actions from followup suggestions
          nextActions = followupActions.filter(a => !executedActionIds.has(a.id))
        }
        if (nextActions.length === 0 && remainingActions.length > 0) {
          // Fall back to remaining actions if no followup suggestions
          nextActions = remainingActions.filter(a => !executedActionIds.has(a.id))
        }
        
        const hasMoreSteps = nextActions.length > 0
        const isLastStep = !hasMoreSteps
        
        // Update remaining actions with smart follow-ups
        if (followupActions.length > 0) {
          // Prioritize result-based suggestions
          const combined = [...followupActions, ...remainingActions]
          const uniqueActions = combined.filter((a, idx) => 
            combined.findIndex(x => x.id === a.id) === idx && !executedActionIds.has(a.id)
          )
          setRemainingActions(uniqueActions.slice(1)) // First one will be suggested next
        }
        
        // Build the response message
        let content = ''
        if (result.success) {
          if (interpretation) {
            content = `✅ **${action.name}** completed!\n\n${interpretation}`
          } else {
            content = `✅ **${action.name}** completed!\n\n\`\`\`\n${outputStr}\n\`\`\``
          }
          
          // Add follow-up reason if available
          if (followupActions.length > 0 && followupActions[0].reason) {
            content += `\n\n💡 *Based on these results: ${followupActions[0].reason}*`
          }
        } else {
          content = `❌ **${action.name}** failed: ${result.message || result.error}`
        }
        
        // Add result message
        const resultMessage = {
          role: 'assistant',
          content,
          timestamp: new Date().toISOString(),
          isActionResult: true,
          actionOutput: result.result?.output,
          actionType: action.id,
          followupActions: followupActions, // Store for reference
          // Always show feedback after action (for both last step and intermediate steps)
          awaitingFeedback: result.success,
          isLastStep: isLastStep
        }
        setMessages(prev => [...prev, resultMessage])
        
        // Set awaiting feedback state
        if (result.success) {
          setAwaitingFeedback(true)
        }
      } catch (error) {
        const errorMessage = {
          role: 'assistant',
          content: `❌ Failed to execute action: ${error.message}`,
          timestamp: new Date().toISOString(),
          isError: true
        }
        setMessages(prev => [...prev, errorMessage])
      } finally {
        setActionExecuting(false)
        setLoading(false)
      }
    } else {
      // Only actions the backend scored carry a remediation_id, and those are
      // rendered by RiskCard, which runs them through the verified path. An
      // action arriving here was refused a risk assessment upstream, so it has
      // no score, no approval token and no way to verify the outcome. Say so
      // rather than running it.
      const reason =
        action.risk_note ||
        'This action was not risk-assessed, so it cannot be run automatically.'
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `🔒 **${action.name}** was not run. ${reason}`,
        timestamp: new Date().toISOString(),
        isError: true
      }])
    }
  }
  
  // Handle user feedback on troubleshooting step
  const handleTroubleshootingFeedback = async (resolved) => {
    setAwaitingFeedback(false)
    
    if (resolved) {
      // User says issue is resolved
      setLoading(true)
      try {
        // Send to LLM for a nice closing response
        const response = await sendChatMessage(
          [...messages, { role: 'user', content: 'Yes, the issue is fixed now. Thank you!' }],
          user.email,
          currentTicket,
          currentSessionId
        )
        const resolvedMessage = {
          role: 'assistant',
          content: response.message || '🎉 Great! I\'m glad that helped resolve your issue. Is there anything else I can help you with?',
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, resolvedMessage])
      } catch (e) {
        const resolvedMessage = {
          role: 'assistant',
          content: '🎉 Great! I\'m glad that helped resolve your issue. Is there anything else I can help you with?',
          timestamp: new Date().toISOString()
        }
        setMessages(prev => [...prev, resolvedMessage])
      } finally {
        setLoading(false)
      }
      // Reset troubleshooting state
      setRemainingActions([])
      setTroubleshootingStep(0)
      setExecutedActionIds(new Set())
    } else {
      // Filter out already executed actions from remaining
      const availableActions = remainingActions.filter(a => !executedActionIds.has(a.id))
      
      // Show next action if available
      if (availableActions.length > 0) {
        const nextAction = availableActions[0]
        const newRemaining = availableActions.slice(1)
        const nextStep = troubleshootingStep + 1
        
        setRemainingActions(newRemaining)
        setTroubleshootingStep(nextStep)
        
        // Build message with reason if available (from result-based suggestions)
        let messageContent = `Okay, let's try something else.`
        if (nextAction.reason) {
          messageContent = `Based on the previous results: *${nextAction.reason}*\n\nLet's try this:`
        }
        
        const nextStepMessage = {
          role: 'assistant',
          content: messageContent,
          timestamp: new Date().toISOString(),
          suggestedActions: [nextAction],
          troubleshootingStep: nextStep,
          totalSteps: nextStep + newRemaining.length
        }
        setMessages(prev => [...prev, nextStepMessage])
      } else {
        // No more actions, escalate to human
        setLoading(true)
        try {
          const response = await sendChatMessage(
            [...messages, { role: 'user', content: 'The issue is still not fixed after trying all the automated fixes.' }],
            user.email,
            currentTicket,
            currentSessionId
          )
          const escalateMessage = {
            role: 'assistant',
            content: response.message || '😔 I\'ve tried all the automated fixes I know. Let me escalate this to our support team for further investigation. They\'ll follow up with you shortly.',
            timestamp: new Date().toISOString()
          }
          setMessages(prev => [...prev, escalateMessage])
        } catch (e) {
          const escalateMessage = {
            role: 'assistant',
            content: '😔 I\'ve tried all the automated fixes I know. Let me escalate this to our support team for further investigation. They\'ll follow up with you shortly.',
            timestamp: new Date().toISOString()
          }
          setMessages(prev => [...prev, escalateMessage])
        } finally {
          setLoading(false)
        }
        setTroubleshootingStep(0)
        setExecutedActionIds(new Set())
      }
    }
  }

  // Handle action approval
  const handleApproveAction = async () => {
    if (!pendingActionRequest) return
    
    setActionExecuting(true)
    try {
      const result = await remediationService.approveAndExecute(pendingActionRequest)
      setActionResult(result)
      
      // Format the output nicely
      let formattedOutput = ''
      if (result.result?.output) {
        const output = result.result.output
        if (typeof output === 'string') {
          formattedOutput = '\n\n' + output
        } else {
          formattedOutput = '\n\n```json\n' + JSON.stringify(output, null, 2) + '\n```'
        }
      }
      
      // Add result as a message
      const resultMessage = {
        role: 'assistant',
        content: result.success 
          ? `✅ **${selectedAction.name}** completed successfully!\n\n${result.message || ''}${formattedOutput}`
          : `❌ **${selectedAction.name}** failed: ${result.message || result.error}`,
        timestamp: new Date().toISOString(),
        isActionResult: true
      }
      setMessages(prev => [...prev, resultMessage])
    } catch (error) {
      setActionResult({ success: false, error: error.message })
    } finally {
      setActionExecuting(false)
    }
  }

  // Handle action cancellation
  const handleCancelAction = async () => {
    if (pendingActionRequest) {
      try {
        await remediationService.reject(pendingActionRequest, 'Declined by user')
      } catch (error) {
        console.warn('Failed to cancel action:', error)
      }
    }
    setShowActionModal(false)
    setSelectedAction(null)
    setPendingActionRequest(null)
    setActionResult(null)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendAll()
    }
  }

  const handleVoiceToggle = () => {
    if (isListening) {
      voiceService.stopListening()
    } else {
      try {
        voiceService.startListening()
      } catch (error) {
        console.error('Error starting voice input:', error)
        const errorMessage = {
          role: 'assistant',
          content: `Unable to start voice input: ${error.message}. Please check your microphone permissions.`,
          timestamp: new Date().toISOString(),
          isError: true
        }
        setMessages(prev => [...prev, errorMessage])
      }
    }
  }

  const handleNewChat = () => {
    // Reset to new chat
    const welcomeMessage = { 
      role: 'assistant', 
      content: `Hi ${user?.name || 'there'}! I'm your AI IT Support Assistant. How can I help you today?`,
      timestamp: new Date().toISOString()
    }
    setMessages([welcomeMessage])
    setCurrentTicket(null)
    setCurrentSessionId(null)  // Reset session ID for new chat
    setExecutedActionIds(new Set())  // Reset executed actions tracker
    setAwaitingFeedback(false)  // Reset feedback state
    setAgentModeTipShown(false)  // Reset agent mode tip for new chat
    clearSelectedImage()
    
    // Clear localStorage for fresh start
    localStorage.removeItem(CHAT_STORAGE_KEY)
    localStorage.removeItem(SESSION_STORAGE_KEY)
    localStorage.removeItem(TICKET_STORAGE_KEY)
    localStorage.removeItem(RESUME_TICKET_KEY)
    
    // Reset backend conversation and get new session ID
    if (user?.email) {
      resetChatConversation(user.email)
        .then(response => {
          if (response?.session_id) {
            setCurrentSessionId(response.session_id)
          }
        })
        .catch(err => console.warn('Could not reset conversation:', err))
    }
  }

  // Image upload handlers
  const handleImageSelect = (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Validate file type
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif']
    if (!validTypes.includes(file.type)) {
      const errorMessage = {
        role: 'assistant',
        content: 'Please select a valid image file (PNG, JPG, JPEG, WEBP, or GIF).',
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
      return
    }

    // Validate file size (max 10MB before compression)
    if (file.size > 10 * 1024 * 1024) {
      const errorMessage = {
        role: 'assistant',
        content: 'Image is too large. Please select an image under 10MB.',
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
      return
    }

    setSelectedImage(file)
    
    // Create preview URL
    const reader = new FileReader()
    reader.onloadend = () => {
      setImagePreview(reader.result)
    }
    reader.readAsDataURL(file)
  }

  const clearSelectedImage = () => {
    setSelectedImage(null)
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleSendWithImage = async () => {
    if (!selectedImage || loading) return

    const userMessage = {
      role: 'user',
      content: input.trim() || 'Please analyze this image and help me troubleshoot the issue.',
      timestamp: new Date().toISOString(),
      imagePreview: imagePreview // Store preview for display
    }

    setMessages(prev => [...prev, userMessage])
    const messageText = input.trim()
    setInput('')
    clearSelectedImage()
    setLoading(true)

    try {
      const response = await sendChatMessageWithImage(
        selectedImage,
        messageText,
        user.email,
        currentTicket,
        currentSessionId
      )
      
      // Build response content with image analysis
      let responseContent = response.message
      if (response.image_analysis) {
        const analysis = response.image_analysis
        responseContent = `**📸 Image Analysis Results:**\n\n`
        responseContent += `**Problem Identified:** ${analysis.issue_description || 'Analysis in progress...'}\n\n`
        if (analysis.extracted_text) {
          responseContent += `**Text/Error Found:** ${analysis.extracted_text}\n\n`
        }
        responseContent += `---\n\n${response.message}`
      }

      const assistantMessage = {
        role: 'assistant',
        content: responseContent,
        timestamp: new Date().toISOString(),
        ticketId: response.ticket_id,
        action: response.action,
        priorityInfo: response.priority_info,
        imageAnalysis: response.image_analysis
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Track session and ticket
      if (response.session_id && !currentSessionId) {
        setCurrentSessionId(response.session_id)
      }
      if (response.ticket_id && !currentTicket) {
        setCurrentTicket(response.ticket_id)
      }

    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error analyzing image: ${error.message}. Please check if the backend is running.`,
        timestamp: new Date().toISOString(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  // Modified handleSend to also handle image uploads
  const handleSendAll = async () => {
    if (selectedImage) {
      await handleSendWithImage()
    } else {
      await handleSend()
    }
  }

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="chat-header-left">
          <Bot size={28} />
          <div>
            <h2>AI Support Chat</h2>
            <div className="chat-status-row">
              <span className={`status-indicator ${backendStatus ? 'online' : 'offline'}`}>
                <span className="status-dot"></span>
                {backendStatus ? 'Online' : 'Offline'}
              </span>
              {currentTicket && (
                <span className="active-ticket-indicator">
                  <FileText size={12} />
                  Ticket #{currentTicket}
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="chat-header-right">
          <div className="agent-mode-toggle" title={agentMode ? "Agent Mode: Actions enabled with permission required" : "Agent Mode: Advice only"}>
            <span className="agent-mode-label">Agent Mode</span>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={agentMode}
                onChange={(e) => setAgentMode(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
            {agentMode && <span className="agent-mode-indicator"><Bot size={18} /></span>}
          </div>
          <button
            onClick={handleNewChat}
            className="new-chat-btn"
            title="Start new chat"
          >
            New Chat
          </button>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message-wrapper ${msg.role}`}>
            <div className="message-bubble">
              <div className="message-header">
                <span className="message-sender">
                  {msg.role === 'user' ? (
                    <><User size={14} /> You</>
                  ) : (
                    <><Bot size={14} /> AI Assistant</>
                  )}
                </span>
                <span className="message-time">
                  {formatTimestamp(msg.timestamp)}
                </span>
              </div>
              <div className="message-text">
                {msg.imagePreview && (
                  <div className="message-image-preview">
                    <img src={msg.imagePreview} alt="Uploaded" />
                  </div>
                )}
                {msg.content}
              </div>
              {msg.ticketId && (
                <div className="message-badges">
                  <span className="badge ticket-badge">
                    <FileText size={12} /> Ticket #{msg.ticketId}
                  </span>
                  {msg.action && (
                    <span className={`badge action-badge ${msg.action}`}>
                      {msg.action === 'escalated' ? <><AlertCircle size={12} /> Escalated</> :
                       msg.action === 'troubleshooting' ? <><Wrench size={12} /> Troubleshooting</> :
                       msg.action === 'clarifying' ? <><HelpCircle size={12} /> Clarifying</> : msg.action}
                    </span>
                  )}
                  {msg.priorityInfo && (
                    <span className={`badge priority-badge ${msg.priorityInfo.priority_label?.toLowerCase()}`}>
                      <Zap size={12} /> {msg.priorityInfo.priority_label}
                    </span>
                  )}
                </div>
              )}
              {/* Agent Mode Suggestion */}
              {msg.agentModeSuggestion && !agentMode && (
                <div className="agent-mode-tip">
                  <div className="tip-content">
                    {msg.agentModeSuggestion}
                  </div>
                  <button 
                    className="enable-agent-mode-btn"
                    onClick={() => setAgentMode(true)}
                  >
                    Enable Agent Mode
                  </button>
                </div>
              )}
              {/* Evidence: which approved KB articles grounded this answer */}
              {msg.citations && msg.citations.length > 0 && (
                <div className="citations">
                  <span className="citations-label">Based on approved knowledge</span>
                  <ul className="citations-list">
                    {msg.citations.map((c) => (
                      <li key={c.kb_id} className="citation">
                        <span className="citation-id">{c.kb_id}</span>
                        <span className="citation-title">{c.title}</span>
                        <span className="citation-score">
                          {Math.round((c.similarity_score || 0) * 100)}% match
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {/* Action Suggestions */}
              {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                <div className="action-suggestions-wrapper">
                  {/* {msg.troubleshootingStep && (
                    <div className="troubleshooting-step-indicator">
                      Step {msg.troubleshootingStep} of {msg.totalSteps}
                    </div>
                  )} */}
                  {msg.suggestedActions
                    .filter((a) => a.risk_level)
                    .map((a) => (
                      <RiskCard
                        key={a.remediation_id || a.id}
                        action={a}
                        onOutcome={(outcome) => handleActionOutcome(a, outcome)}
                      />
                    ))}
                  <ActionSuggestions 
                    suggestions={msg.suggestedActions.filter((a) => !a.risk_level)}
                    onSelectAction={handleSelectAction}
                    userEmail={user?.email}
                  />
                </div>
              )}
              {/* Feedback buttons for step-by-step troubleshooting */}
              {msg.awaitingFeedback && awaitingFeedback && (
                <div className="troubleshooting-feedback">
                  <p className="feedback-question">Did this help resolve your issue?</p>
                  <div className="feedback-buttons">
                    <button 
                      className="feedback-btn yes"
                      onClick={() => handleTroubleshootingFeedback(true)}
                    >
                      <CheckCircle size={16} /> Yes, it's fixed!
                    </button>
                    <button 
                      className="feedback-btn no"
                      onClick={() => handleTroubleshootingFeedback(false)}
                    >
                      <XCircle size={16} /> {msg.isLastStep || remainingActions.length === 0 
                        ? 'No, escalate to support' 
                        : 'No, try next step'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message-wrapper assistant">
            <div className="message-bubble">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        {isListening && (
          <div className="voice-listening-indicator">
            <div className="voice-pulse"></div>
            <span>{interimTranscript || 'Listening... Speak now'}</span>
          </div>
        )}
        {imagePreview && (
          <div className="image-preview-container">
            <img src={imagePreview} alt="Selected" className="image-preview" />
            <button 
              onClick={clearSelectedImage} 
              className="clear-image-btn"
              title="Remove image"
            >
              <X size={16} />
            </button>
            <span className="image-preview-label">Image attached</span>
          </div>
        )}
        <div className="input-section">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleImageSelect}
            accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
            style={{ display: 'none' }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={loading || isListening}
            className={`image-upload-btn ${selectedImage ? 'has-image' : ''}`}
            title="Upload image (screenshot, error message, device photo)"
          >
            <Image size={20} />
          </button>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={selectedImage ? "Describe the issue shown in the image (optional)..." : isListening ? "Listening..." : "Describe your IT issue... (e.g., 'My laptop is slow')"}
            className="message-input"
            rows={2}
            disabled={loading || isListening}
          />
          {voiceSupported && (
            <button
              onClick={handleVoiceToggle}
              disabled={loading}
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              title={isListening ? 'Stop listening' : 'Start voice input'}
            >
              {isListening ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
          )}
          <button 
            onClick={handleSendAll} 
            disabled={loading || (!input.trim() && !selectedImage) || isListening}
            className="send-btn"
          >
            <Send size={18} />
            <span>Send</span>
          </button>
        </div>
        <div className="input-hint">
          {voiceSupported ? (
            <>
              Press Enter to send, Shift+Enter for new line • Click <Mic size={14} style={{ display: 'inline', verticalAlign: 'middle' }} /> for voice • Click <Image size={14} style={{ display: 'inline', verticalAlign: 'middle' }} /> to upload image
            </>
          ) : (
            <>
              Press Enter to send, Shift+Enter for new line • Click <Image size={14} style={{ display: 'inline', verticalAlign: 'middle' }} /> to upload image
            </>
          )}
        </div>
      </div>

      {/* Action Approval Modal */}
      <ActionModal
        isOpen={showActionModal}
        onClose={() => {
          setShowActionModal(false)
          setSelectedAction(null)
          setPendingActionRequest(null)
          setActionResult(null)
        }}
        action={selectedAction}
        onApprove={handleApproveAction}
        onCancel={handleCancelAction}
        isExecuting={actionExecuting}
        result={actionResult}
      />
    </div>
  )
}

function MainLayout({ user, onLogout }) {
  return (
    <div className="main-layout">
      <Sidebar user={user} onLogout={onLogout} />
      <div className="main-content">
        <Routes>
          <Route path="/dashboard" element={<Dashboard user={user} />} />
          <Route path="/quick-actions" element={<QuickActionsPage />} />
          <Route path="/chat" element={<ChatPage user={user} />} />
          <Route path="/tickets" element={<TicketList />} />
          <Route path="/monitoring" element={<SystemMonitoring />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/automation" element={<AutomationPage />} />
          <Route path="/error-codes" element={<ErrorCodesPage />} />
          <Route path="/knowledge-base" element={<KnowledgeBasePage />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="/audit-logs" element={<AuditLogs user={user} />} />
          <Route path="/settings" element={<Settings user={user} />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </div>
  )
}

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Load primary color on app initialization
  useEffect(() => {
    const savedColor = localStorage.getItem('primaryColor')
    if (savedColor) {
      const root = document.documentElement
      root.style.setProperty('--color-primary', savedColor)
      
      // Adjust hover color
      const hexToRgb = (hex) => {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
        return result ? {
          r: parseInt(result[1], 16),
          g: parseInt(result[2], 16),
          b: parseInt(result[3], 16)
        } : { r: 20, g: 184, b: 166 }
      }
      
      const rgb = hexToRgb(savedColor)
      const hoverColor = `rgb(${Math.max(0, rgb.r - 20)}, ${Math.max(0, rgb.g - 20)}, ${Math.max(0, rgb.b - 20)})`
      root.style.setProperty('--color-primary-hover', hoverColor)
    }
  }, [])

  useEffect(() => {
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER_DATA)
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser))
      } catch (error) {
        console.error('Failed to parse stored user data:', error)
        localStorage.removeItem(STORAGE_KEYS.USER_DATA)
        localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
      }
    }
    setLoading(false)
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USER_DATA)
    setUser(null)
  }

  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        background: 'var(--color-bg-primary)',
        color: 'var(--color-text-primary)'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '24px', marginBottom: '16px' }}>Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <Router>
      {!user ? (
        <Routes>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      ) : (
        <MainLayout user={user} onLogout={handleLogout} />
      )}
    </Router>
  )
}

export default App
