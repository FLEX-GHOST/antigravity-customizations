---
name: haskell-pure-architecture
description: Authoritative guide for pure functional programming with Haskell, GHC extensions, Monad transformers (MTL), Category Theory constructs, and Cabal.
language: haskell
category: programming-languages
quality_score: 100
tier: official
triggers:
  - haskell
  - ghc
  - monad
  - cabal
  - pure functional
  - typeclass
  - stack
---
# Haskell Pure Functional Architecture & Typeclass Engineering

Guidelines for building formally verifiable, pure functional software with Haskell.

## 1. Purity & Monadic Design
* **Total Functions**: Avoid partial functions (like `head` or `read`); always return `Maybe` or `Either` to handle invalid inputs safely.
* **MTL & ReaderT Pattern**: Structure application state, database access, and logging using the ReaderT design pattern over concrete IO.
  ```haskell
  {-# LANGUAGE GeneralizedNewtypeDeriving #-}
  module Core.Service where

  import Control.Monad.Reader
  import Data.Text (Text)

  data Env = Env { dbConn :: Text, apiSecret :: Text }

  newtype AppM a = AppM { runAppM :: ReaderT Env IO a }
    deriving (Functor, Applicative, Monad, MonadReader Env, MonadIO)
  ```

## 2. High-Assurance Type Systems
* **Newtype Wrapping**: Never pass raw primitive types (`Text`, `Int`) across domain boundaries. Wrap them in `newtype` identifiers to eliminate semantic confusion.
