/**
 * Oh My Pi Hook / Extension: Post-Feature Delivery Reminder
 * At agent_end, lists uncommitted changes so the final report can mention them.
 * Per CLAUDE.md, the agent must NOT commit or push on its own — this is only a reminder.
 */

interface ExtensionContext {
  on(event: string, handler: () => Promise<void> | void): void;
  exec(command: string): Promise<{ stdout?: string; stderr?: string; exitCode?: number }>;
  logger: {
    warn(msg: string): void;
    info(msg: string): void;
    error(msg: string): void;
  };
}

export default function postFeatureDeliveryHook(pi: ExtensionContext): void {
  pi.on("agent_end", async () => {
    try {
      const res = await pi.exec("git status --porcelain");
      const uncommitted = (res?.stdout || "").trim();
      if (uncommitted.length > 0) {
        pi.logger.info(
          "[HOOK post-feature-delivery] Uncommitted changes:\n" +
          uncommitted +
          "\n-> Report them and the test result; commit/push only when the user asks (CLAUDE.md)." +
          " After deploy: restart agentfx.service (app/templates/static) or the affected cbot container (cBot/*.cs)."
        );
      }
    } catch (e) {
      // non-blocking
    }
  });
}
