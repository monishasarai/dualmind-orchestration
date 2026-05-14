import { useState } from 'react'
import PropTypes from 'prop-types'
// @ts-ignore - consuming shared markdown renderer
import LLMMessage from './LLMMessage'
import ExecutionDetailsPanel from './ExecutionDetailsPanel'
import { hasExecutionDetailsData } from '../utils/executionDetails'

/**
 * MessageTabs Component
 *
 * Provides a two-tab layout for assistant messages so users can switch
 * between the synthesized answer and the execution details metadata.
 * Styling matches the dark theme with rounded edges and subtle borders.
 */
const MessageTabs = ({
  answer,
  executionDetails,
  fallbackUsed,
  fallbackReason,
  fallbackSource,
}) => {
  const [activeTab, setActiveTab] = useState('answer')
  const tabs = [
    { id: 'answer', label: 'Answer' },
    { id: 'details', label: 'Execution Details' },
  ]

  const hasDetails = hasExecutionDetailsData(executionDetails)

  if (!hasDetails) {
    return (
      <div className="mt-2 space-y-3">
        {fallbackUsed ? (
          <div className="rounded-md border border-aqua/40 bg-aqua/5 px-3 py-2 text-xs text-aqua">
            Using fallback response
            {fallbackReason ? ` (${fallbackReason.replace(/_/g, ' ')})` : ''}{' '}
            {fallbackSource ? `via ${fallbackSource}` : ''}
          </div>
        ) : null}
        <LLMMessage content={answer} className="text-sm" />
      </div>
    )
  }

  return (
    <div className="mt-2">
      <div className="flex items-stretch rounded-t-lg border border-dark-border bg-dark-surface/60 backdrop-blur">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 px-4 py-2 text-sm font-medium transition-colors duration-200
                ${isActive ? 'bg-dark-surface text-text-primary' : 'text-text-secondary hover:text-text-primary'}
                ${!hasDetails && tab.id === 'details' ? 'cursor-not-allowed opacity-40' : ''}
              `}
              disabled={tab.id === 'details' && !hasDetails}
            >
              {tab.label}
            </button>
          )
        })}
      </div>

      <div className="rounded-b-lg border border-t-0 border-dark-border bg-dark-surface p-4">
        {activeTab === 'answer' ? (
          <div className="space-y-3">
            {fallbackUsed ? (
              <div className="rounded-md border border-aqua/40 bg-aqua/5 px-3 py-2 text-xs text-aqua">
                Using fallback response
                {fallbackReason ? ` (${fallbackReason.replace(/_/g, ' ')})` : ''}{' '}
                {fallbackSource ? `via ${fallbackSource}` : ''}
              </div>
            ) : null}
            <LLMMessage content={answer} className="text-sm" />
          </div>
        ) : (
          <ExecutionDetailsPanel details={executionDetails} />
        )}
      </div>
    </div>
  )
}

MessageTabs.propTypes = {
  answer: PropTypes.string.isRequired,
  executionDetails: PropTypes.object,
  fallbackUsed: PropTypes.bool,
  fallbackReason: PropTypes.string,
  fallbackSource: PropTypes.string,
}

MessageTabs.defaultProps = {
  executionDetails: null,
  fallbackUsed: false,
  fallbackReason: null,
  fallbackSource: null,
}

export default MessageTabs

