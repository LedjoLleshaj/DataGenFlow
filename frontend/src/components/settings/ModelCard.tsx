import type { ReactNode } from "react";
import { Box, Text, Button, IconButton, Spinner, Tooltip } from "@primer/react";
import {
  TrashIcon,
  PencilIcon,
  CheckCircleIcon,
  CheckCircleFillIcon,
  StarIcon,
} from "@primer/octicons-react";
import type { LLMModelConfig, EmbeddingModelConfig } from "../../types";

interface ModelCardStatus {
  isDefault: boolean;
  isTesting: boolean;
  isSettingDefault: boolean;
}

interface ModelCardActions {
  onSetDefault: () => void;
  onTest: () => void;
  onEdit: () => void;
  onDelete: () => void;
}

interface ModelCardProps<T extends LLMModelConfig | EmbeddingModelConfig> {
  model: T;
  status: ModelCardStatus;
  actions: ModelCardActions;
  extraDetails?: ReactNode;
}

export function ModelCard<T extends LLMModelConfig | EmbeddingModelConfig>({
  model,
  status,
  actions,
  extraDetails,
}: ModelCardProps<T>) {
  const { isDefault, isTesting, isSettingDefault } = status;
  const { onSetDefault, onTest, onEdit, onDelete } = actions;

  return (
    <Box
      sx={{
        p: 3,
        border: "1px solid",
        borderColor: "border.default",
        borderRadius: 2,
        bg: "canvas.subtle",
        transition: "all 0.2s",
      }}
    >
      <Box sx={{ display: "flex", alignItems: "start", justifyContent: "space-between" }}>
        <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {/* name and badges row */}
          <Box sx={{ display: "flex", alignItems: "center", gap: 2, mb: 1 }}>
            <Text sx={{ fontWeight: "bold", fontSize: 2, color: "fg.default" }}>{model.name}</Text>
            <Box
              sx={{
                px: 2,
                py: 1,
                borderRadius: 2,
                bg: "accent.subtle",
                color: "accent.fg",
                fontSize: 0,
                fontWeight: "semibold",
              }}
            >
              {model.provider}
            </Box>
            {/* isDefault renders the default badge with CheckCircleFillIcon to visually distinguish the selected model */}
            {isDefault && (
              <Box
                sx={{
                  px: 2,
                  py: 1,
                  borderRadius: 2,
                  border: "1px solid",
                  borderColor: "success.emphasis",
                  color: "success.fg",
                  fontSize: 0,
                  fontWeight: "semibold",
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                }}
              >
                <CheckCircleFillIcon size={12} />
                Default
              </Box>
            )}
          </Box>

          {/* model details - model.model_name and model.endpoint; extraDetails may be appended for additional info like embedding dimensions */}
          <Text sx={{ fontSize: 1, color: "fg.muted", mb: 1 }}>
            model: {model.model_name}
            {extraDetails}
          </Text>
          <Text sx={{ fontSize: 1, color: "fg.muted", fontFamily: "mono" }}>{model.endpoint}</Text>
        </Box>

        {/* action buttons */}
        <Box sx={{ display: "flex", gap: 2 }}>
          {!isDefault && (
            <Tooltip aria-label="Set as default model" direction="s">
              <Button
                size="small"
                variant="default"
                onClick={onSetDefault}
                disabled={isSettingDefault}
                sx={{
                  color: "attention.fg",
                  borderColor: "attention.emphasis",
                  "&:hover:not(:disabled)": {
                    bg: "attention.subtle",
                    borderColor: "attention.emphasis",
                    color: "attention.fg",
                  },
                }}
              >
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  {isSettingDefault ? <Spinner size="small" /> : <StarIcon size={16} />}
                  <Text>{isSettingDefault ? "Setting..." : "Set Default"}</Text>
                </Box>
              </Button>
            </Tooltip>
          )}
          <Button
            size="small"
            variant="default"
            onClick={onTest}
            disabled={isTesting}
            sx={{
              color: isTesting ? "fg.muted" : "success.fg",
              borderColor: isTesting ? "border.default" : "success.emphasis",
              "&:hover:not(:disabled)": {
                bg: "success.subtle",
                borderColor: "success.emphasis",
                color: "success.fg",
              },
            }}
          >
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              {isTesting ? <Spinner size="small" /> : <CheckCircleIcon size={16} />}
              <Text>{isTesting ? "Testing..." : "Test"}</Text>
            </Box>
          </Button>
          <IconButton icon={PencilIcon} aria-label="edit" size="small" onClick={onEdit} />
          <IconButton
            icon={TrashIcon}
            aria-label="delete"
            size="small"
            variant="danger"
            onClick={onDelete}
          />
        </Box>
      </Box>
    </Box>
  );
}
