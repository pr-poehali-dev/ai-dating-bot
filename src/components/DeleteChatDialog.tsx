import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import Icon from "@/components/ui/icon";

interface DeleteChatDialogProps {
  isOpen: boolean;
  girlName: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const DeleteChatDialog = ({ isOpen, girlName, onConfirm, onCancel }: DeleteChatDialogProps) => {
  return (
    <AlertDialog open={isOpen} onOpenChange={onCancel}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className="flex items-center gap-2">
            <Icon name="Trash2" size={24} className="text-destructive" />
            Удалить диалог?
          </AlertDialogTitle>
          <AlertDialogDescription className="text-base">
            Вся история переписки с <span className="font-semibold">{girlName}</span> будет безвозвратно удалена.
            <br />
            <br />
            Это действие нельзя отменить.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Отмена</AlertDialogCancel>
          <AlertDialogAction
            onClick={onConfirm}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            <Icon name="Trash2" size={16} className="mr-2" />
            Удалить
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default DeleteChatDialog;