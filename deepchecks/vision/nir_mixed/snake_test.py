import os
import albumentations as A
from albumentations.pytorch import ToTensorV2
from pytorch_lightning import Trainer
import torch

# Local
from deepchecks.vision.nir_mixed.snake_data_module import SnakeDataModule
from deepchecks.vision.nir_mixed.snake_lit_module import SnakeLitModule

ckpt_path = "~/code/DeepChecks/deepchecks/workdir/version_1/last.ckpt"
batch_size = 256
num_workers = 4
# validation has center crop, train has random crop + flip, otherwise same
val_transforms = A.Compose([
    A.SmallestMaxSize(max_size=256),
    A.CenterCrop(height=224, width=224),
    A.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
    ToTensorV2(),
])

snake_test_module = SnakeDataModule(data_dir=os.path.expanduser("~/code/DeepChecks/deepchecks/workdir/version_1/val"),
                               batch_size=batch_size,
                               val_transforms=val_transforms,
                               num_workers=num_workers)
net = SnakeLitModule(num_classes=snake_test_module.num_classes,
                     optimizer="adam",
                     finetune_last=True,
                     )
net = net.load_from_checkpoint(checkpoint_path=ckpt_path, num_classes=snake_test_module.num_classes)
# Test
snake_test_dataloader = snake_test_module.test_dataloader()
trainer = Trainer(gpus=1)
test_result = trainer.test(net, dataloaders=snake_test_dataloader)
# result = trainer.predict(net, dataloaders=snake_test_dataloader)

