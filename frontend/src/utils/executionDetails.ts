import type { ExecutionDetails } from '../types'

const stringHasContent = (value: unknown): boolean =>
  typeof value === 'string' && value.trim().length > 0

const objectHasKeys = (value: unknown): boolean =>
  !!value && typeof value === 'object' && Object.keys(value as Record<string, unknown>).length > 0

export const hasExecutionDetailsData = (details?: ExecutionDetails | null): boolean => {
  if (!details) return false

  const record = details as Record<string, unknown>

  const planOverview =
    record.planOverview ??
    record.plan_overview ??
    details.planSummary ??
    (details.plan && (details.plan as Record<string, unknown>).summary)

  const executionSteps = details.executionSteps ?? record.execution_steps
  const expectedOutput = record.expectedOutput ?? record.expected_output ?? null
  const summaryText = details.summary ?? null
  const reasoningText = details.reasoning ?? null
  const verificationText = details.verification ?? null
  const finalVerification = details.finalVerification ?? null
  const fallbacks = details.fallbacks ?? null
  const metadata = details.metadata ?? null

  const hasPlanOverview = stringHasContent(planOverview)
  const hasExecutionSteps = Array.isArray(executionSteps) && executionSteps.length > 0
  const hasExpectedOutput = stringHasContent(expectedOutput)
  const hasReasoning = stringHasContent(reasoningText)
  const hasVerification = stringHasContent(verificationText)
  const hasFinalVerification = objectHasKeys(finalVerification)
  const hasFallbacks = objectHasKeys(fallbacks)

  const structuredInfo =
    hasPlanOverview ||
    hasExecutionSteps ||
    hasExpectedOutput ||
    hasReasoning ||
    hasVerification ||
    hasFinalVerification ||
    hasFallbacks

  if (structuredInfo) {
    return true
  }

  const metadataRecord = (metadata ?? null) as Record<string, unknown> | null
  const isLightweight = Boolean(metadataRecord && metadataRecord.lightweightMode)

  const metadataSignals = Boolean(
    metadataRecord &&
      (metadataRecord.executionTime != null ||
        metadataRecord.iterations != null ||
        metadataRecord.planScore != null ||
        metadataRecord.planApproved != null ||
        metadataRecord.fallbackUsed === true ||
        stringHasContent(metadataRecord.fallbackReason) ||
        stringHasContent(metadataRecord.fallbackSource)),
  )

  if (metadataSignals && !isLightweight) {
    return true
  }

  if (stringHasContent(summaryText) && !isLightweight) {
    return true
  }

  return false
}
