

import argparse
import torch
import logging
import sys
import os

sys.path.append(f'{os.path.dirname(os.path.realpath(__file__))}/ru_gpts/')

from modules.text_generator.ru_gpts.generate_transformers import (set_seed,
                                            MODEL_CLASSES,
                                            adjust_length_to_model,
                                            PREPROCESSING_FUNCTIONS,

                                            )

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO,
)
logger = logging.getLogger(__name__)


class GPT3Generator:
    @staticmethod
    def get_default_args(parser):
        args_str = "--model_type gpt2 --model_name_or_path sberbank-ai/rugpt3small_based_on_gpt2 --k 10 --p 0.9"
        args = parser.parse_args(args_str.split())
        return args

    @staticmethod
    def add_args(parser):
        parser.add_argument(
            "--model_type",
            default="gpt2",
            type=str,
            help="Model type selected in the list: " + ", ".join(MODEL_CLASSES.keys()),
        )
        parser.add_argument(
            "--model_name_or_path",
            default="sberbank-ai/rugpt3small_based_on_gpt2",
            type=str,
            help="Path to pre-trained model or shortcut name selected in the list: " + ", ".join(MODEL_CLASSES.keys()),
        )

        parser.add_argument("--prompt", type=str, default="")
        parser.add_argument("--length", type=int, default=20)
        parser.add_argument("--stop_token", type=str, default="</s>", help="Token at which text generation is stopped")

        parser.add_argument(
            "--temperature",
            type=float,
            default=1.0,
            help="temperature of 1.0 has no effect, lower tend toward greedy sampling",
        )
        parser.add_argument(
            "--repetition_penalty", type=float, default=1.0,
            help="primarily useful for CTRL model; in that case, use 1.2"
        )
        parser.add_argument("--k", type=int, default=10)
        parser.add_argument("--p", type=float, default=0.9)

        parser.add_argument("--padding_text", type=str, default="", help="Padding text for Transfo-XL and XLNet.")
        parser.add_argument("--xlm_language", type=str, default="",
                            help="Optional language when used with the XLM model.")

        parser.add_argument("--seed", type=int, default=42, help="random seed for initialization")
        parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")
        parser.add_argument("--num_return_sequences", type=int, default=1, help="The number of samples to generate.")

    def __init__(self, args):
        self.args = args
        assert self.args.num_return_sequences == 1, RuntimeError("Wrong num_return_sequences")

        args.device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
        args.n_gpu = 0 if args.no_cuda else torch.cuda.device_count()

        set_seed(args)

        # Initialize the model and tokenizer
        try:
            args.model_type = args.model_type.lower()
            model_class, tokenizer_class = MODEL_CLASSES[args.model_type]
        except KeyError:
            raise KeyError("the model {} you specified is not supported. You are welcome to add it and open a PR :)")

        self.tokenizer = tokenizer_class.from_pretrained(args.model_name_or_path)
        self.model = model_class.from_pretrained(args.model_name_or_path)
        self.model.to(args.device)
        args.length = adjust_length_to_model(args.length, max_sequence_length=self.model.config.max_position_embeddings)

    def generate_next(self, prompt_text):
        if prompt_text == "stop" or prompt_text.strip()=='':
            return
        # Different models need different input formatting and/or extra arguments
        requires_preprocessing = self.args.model_type in PREPROCESSING_FUNCTIONS.keys()
        if requires_preprocessing:
            prepare_input = PREPROCESSING_FUNCTIONS.get(self.args.model_type)
            preprocessed_prompt_text = prepare_input(self.args, self.model, self.tokenizer, prompt_text)
            encoded_prompt = self.tokenizer.encode(
                preprocessed_prompt_text, add_special_tokens=False, return_tensors="pt",
                add_space_before_punct_symbol=True
            )
        else:
            encoded_prompt = self.tokenizer.encode(prompt_text, add_special_tokens=False, return_tensors="pt")
        encoded_prompt = encoded_prompt.to(self.args.device)

        output_sequences = self.model.generate(
            input_ids=encoded_prompt,
            max_length=self.args.length + len(encoded_prompt[0]),
            temperature=self.args.temperature,
            top_k=self.args.k,
            top_p=self.args.p,
            repetition_penalty=self.args.repetition_penalty,
            do_sample=True,
            num_return_sequences=self.args.num_return_sequences,
        )

        # Remove the batch dimension when returning multiple sequences
        if len(output_sequences.shape) > 2:
            output_sequences.squeeze_()

        #for generated_sequence_idx, generated_sequence in enumerate(output_sequences):

        generated_sequence = output_sequences[0]
        generated_sequence = generated_sequence.tolist()

        # Decode text
        text = self.tokenizer.decode(generated_sequence, clean_up_tokenization_spaces=True)

        # Remove all text after the stop token
        text = text[: text.find(self.args.stop_token) if self.args.stop_token else None]

        # Add the prompt at the beginning of the sequence. Remove the excess text that was used for pre-processing
        total_sequence = (
                prompt_text + text[len(self.tokenizer.decode(encoded_prompt[0], clean_up_tokenization_spaces=True)):]
        )
        # os.system('clear')
        logger.info("ruGPT:" + total_sequence)

        return total_sequence


def main():
    parser = argparse.ArgumentParser()
    GPT3Generator.add_args(parser)

    # Loading default options
    # args = GPT3Generator.get_default_args(parser)
    args = parser.parse_args()

    generator = GPT3Generator(args)
    logger.info(args)
    while True:
        context = input("Context>>>")
        text = generator.generate_next(context)
        if text is None:
            logger.info("End.")
            break


if __name__ == "__main__":
    main()
